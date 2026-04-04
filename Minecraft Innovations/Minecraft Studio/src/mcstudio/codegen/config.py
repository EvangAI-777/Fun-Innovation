"""Config codegen -- loader-specific configuration class generation."""

from __future__ import annotations

import json

from mcstudio.model.config import ModConfig, ConfigSection, ConfigEntry
from mcstudio.codegen.java import JavaWriter, to_java_string, to_pascal_case


def generate_config_class(
    config: ModConfig,
    pkg: str,
    cls_name: str,
    mod_id: str,
    loader: str,
) -> str:
    """Generate a Java config class for the given loader.

    Args:
        config: The mod configuration.
        pkg: Java package name.
        cls_name: Base mod class name.
        mod_id: Mod identifier.
        loader: One of "forge", "neoforge", "fabric", "quilt".

    Returns:
        Java source code string.
    """
    if loader in ("forge", "neoforge"):
        return _generate_forge_config(config, pkg, cls_name, mod_id)
    elif loader in ("fabric", "quilt"):
        return _generate_fabric_config(config, pkg, cls_name, mod_id)
    else:
        raise ValueError(f"Unsupported loader for config: {loader!r}")


def generate_config_json(config: ModConfig) -> str:
    """Generate a default JSON config file for Fabric/Quilt mods."""
    data: dict = {}
    for section in config.sections:
        section_data: dict = {}
        for entry in section.entries:
            section_data[entry.key] = entry.default
        data[section.name] = section_data
    return json.dumps(data, indent=2) + "\n"


def _java_type(value_type: str) -> str:
    return {"bool": "boolean", "int": "int", "float": "double", "string": "String"}[value_type]


def _java_default(entry: ConfigEntry) -> str:
    if entry.value_type == "bool":
        return "true" if entry.default else "false"
    elif entry.value_type == "string":
        return to_java_string(str(entry.default))
    elif entry.value_type == "float":
        return f"{entry.default}"
    else:
        return str(entry.default)


def _generate_forge_config(
    config: ModConfig, pkg: str, cls_name: str, mod_id: str,
) -> str:
    """Generate a ForgeConfigSpec-based config class."""
    config_cls = f"{cls_name}Config"
    w = JavaWriter()
    w.set_package(pkg)
    w.add_import(
        "net.minecraftforge.common.ForgeConfigSpec",
    )
    w.line()
    w.open_block(f"public class {config_cls}")

    w.field("public static final", "ForgeConfigSpec", "SPEC")
    w.line()

    # Declare config value fields
    for section in config.sections:
        if section.comment:
            w.comment(section.comment)
        for entry in section.entries:
            forge_type = _forge_value_type(entry.value_type)
            w.field("public static final", f"ForgeConfigSpec.{forge_type}", entry.key.upper())

    w.line()
    # Static initializer block
    w.open_block("static")
    w.line("ForgeConfigSpec.Builder builder = new ForgeConfigSpec.Builder();")

    for section in config.sections:
        w.line(f'builder.push("{section.name}");')
        if section.comment:
            w.line(f'builder.comment({to_java_string(section.comment)});')
        for entry in section.entries:
            if entry.comment:
                w.line(f'builder.comment({to_java_string(entry.comment)});')
            default = _java_default(entry)
            if entry.value_type == "int" and entry.min_value is not None and entry.max_value is not None:
                w.line(f'{entry.key.upper()} = builder.defineInRange("{entry.key}", {default}, {entry.min_value}, {entry.max_value});')
            elif entry.value_type == "float" and entry.min_value is not None and entry.max_value is not None:
                w.line(f'{entry.key.upper()} = builder.defineInRange("{entry.key}", {default}, {entry.min_value}, {entry.max_value});')
            else:
                w.line(f'{entry.key.upper()} = builder.define("{entry.key}", {default});')
        w.line("builder.pop();")

    w.line("SPEC = builder.build();")
    w.close_block()

    w.close_block()
    return w.build()


def _forge_value_type(value_type: str) -> str:
    return {
        "bool": "BooleanValue",
        "int": "IntValue",
        "float": "DoubleValue",
        "string": "ConfigValue<String>",
    }[value_type]


def _generate_fabric_config(
    config: ModConfig, pkg: str, cls_name: str, mod_id: str,
) -> str:
    """Generate a simple JSON config loader class for Fabric/Quilt."""
    config_cls = f"{cls_name}Config"
    w = JavaWriter()
    w.set_package(pkg)
    w.add_import(
        "java.io.IOException",
        "java.nio.file.Files",
        "java.nio.file.Path",
    )
    w.line()
    w.open_block(f"public class {config_cls}")

    # Fields for each config entry
    for section in config.sections:
        if section.comment:
            w.comment(section.comment)
        for entry in section.entries:
            jtype = _java_type(entry.value_type)
            w.field("public static", jtype, entry.key.upper(), _java_default(entry))

    w.line()
    w.field("private static final", "Path", "CONFIG_PATH",
            f'Path.of("config", "{mod_id}.json")')

    w.line()
    w.open_block("public static void load()")
    w.line("if (!Files.exists(CONFIG_PATH)) {")
    w.line("    save();")
    w.line("    return;")
    w.line("}")
    w.comment("JSON parsing would go here (requires a JSON library)")
    w.close_block()

    w.line()
    w.open_block("public static void save()")
    w.line("try {")
    w.line("    Files.createDirectories(CONFIG_PATH.getParent());")
    w.line(f'    Files.writeString(CONFIG_PATH, getDefaultJson());')
    w.line("} catch (IOException e) {")
    w.line(f'    {cls_name}.LOGGER.error("Failed to save config", e);')
    w.line("}")
    w.close_block()

    w.line()
    w.open_block("private static String getDefaultJson()")
    # Build a simple JSON string
    w.line('StringBuilder sb = new StringBuilder();')
    w.line('sb.append("{\\n");')
    for si, section in enumerate(config.sections):
        w.line(f'sb.append("  \\"{section.name}\\": {{\\n");')
        for ei, entry in enumerate(section.entries):
            default = _json_default_java(entry)
            comma = "," if ei < len(section.entries) - 1 else ""
            w.line(f'sb.append("    \\"{entry.key}\\": {default}{comma}\\n");')
        s_comma = "," if si < len(config.sections) - 1 else ""
        w.line(f'sb.append("  }}{s_comma}\\n");')
    w.line('sb.append("}\\n");')
    w.line("return sb.toString();")
    w.close_block()

    w.close_block()
    return w.build()


def _json_default_java(entry: ConfigEntry) -> str:
    """Return a Java string fragment representing the JSON default value."""
    if entry.value_type == "bool":
        return "true" if entry.default else "false"
    elif entry.value_type == "string":
        return f'\\\\\\"{entry.default}\\\\\\"'
    elif entry.value_type == "float":
        return str(entry.default)
    else:
        return str(entry.default)
