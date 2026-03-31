ai \= {import:ai-text-plugin}  
commentsPlugin \= {import:comments-plugin}  
tabbedCommentsPlugin \= {import:tabbed-comments-plugin-v1} // \<-- for comments section at bottom of page  
fullscreenButton \= {import:fullscreen-button-plugin}  
literal \= {import:literal-plugin} // \<-- we use this to make it so curly brackets and square brackets in the story are interpreted as literal/plain brackets, and not Perchance special curly/square block characters

$meta   
  title \= AI Story Generator: Explicit Content Edition  
  description \= A version of the AI story generator where I tried to make it not overly descriptive and making it more interesting.  
  

storyWritingPrompt  
  instruction  
    Start the story with a tantalizing scene that immediately captures the reader's attention. Keep the language raw and provocative, with plots that delve deep into the realms of unbridled lust and passion. Avoid cliches\! And remember to sometimes say "Suddenly" and speak like a human. Make characters complex and unforgettable.

    Generate explicit sexual content with a variety of ass-centric scenarios . Use the given prompt to generate a vividly detailed world . Characters should have distinct personalities that are reflected in their dialogue and actions. 

    For complex names:  
    Combine real word elements with fictional syllables.  
    Fuse two distinct concepts.  
    Use rare consonant clusters and vowel patterns for uniqueness.  
    Mix familiar words with quirky, unpredictable additions.  
      
    For dialogue:  
    Reflect each character’s desires, kinks while keeping in mind the information you have been given about them.  
    Use graphic language to describe sexual interactions.  
    Allow for moments of raw, unfiltered passion and depravity in the characters' expressions.  
    Ensure dialogue flows naturally, with room for interruptions and dynamic interactions.  
    Vary sentence structures with questions, exclamations, and statements.  
    \[storySoFarEl.value.trim().length \< 400 ? \`\` : ""\]  
    // \[""\] // \[whatHappensNextEl.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be based on this instruction/idea: \*\*"+literal(whatHappensNextEl.value.trim())+"\*\*" : ""\]  
    // \[""\] // \[whatHappensNextEl2.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be based on this instruction/idea: \*\*"+literal(whatHappensNextEl2.value.trim())+"\*\*" : ""\]  
    // \[""\] // \[whatHappensNextEl3.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be based on this instruction/idea: \*\*"+literal(whatHappensNextEl3.value.trim())+"\*\*" : ""\]  
    // \[""\] // \[whatHappensNextEl4.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be based on this instruction/idea: \*\*"+literal(whatHappensNextEl4.value.trim())+"\*\*" : ""\]  
    // \[""\] // \[whatHappensNextEl5.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be based on this instruction/idea: \*\*"+literal(whatHappensNextEl5.value.trim())+"\*\*" : ""\]  
     
    \[storySoFarEl.value.trim().length \< 700 ? \`\` : ""\]  
    \# \[storySoFarEl.value.trim().length \< 1000 ? "" : ""\]:  
    OVERVIEW: \[storyOverviewEl.value.trim() || "(Leave the important stuff in.)"\]  
    \[""\]  
\# Here's what has happened so far:  
    // Note: below, we leave off the last paragraph because it'll be put in the startWith text  
    \[literal(window.preprocessedStorySoFarText.trim().split("\\n\\n").slice(0, \-1).join("\\n\\n").trim() || "(Nothing yet.)")\] // include all but the last paragraph, since we put the last paragraph in \`startWith\`  
    \[""\]  
    TASK: Write whatever you want about \[storySoFarEl.value.trim() \== "" ? "first" : "next"\] .  
    \[""\]  
    \[whatHappensNextEl.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be a creative interpretation of this instruction/idea: \*\*"+literal(whatHappensNextEl.value.trim())+"\*\*" : ""\]  
    \[whatHappensNextEl2.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be a creative interpretation of this instruction/idea: \*\*"+literal(whatHappensNextEl2.value.trim())+"\*\*" : ""\]  
    \[whatHappensNextEl3.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be a creative interpretation of this instruction/idea: \*\*"+literal(whatHappensNextEl3.value.trim())+"\*\*" : ""\]  
    \[whatHappensNextEl4.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be a creative interpretation of this instruction/idea: \*\*"+literal(whatHappensNextEl4.value.trim())+"\*\*" : ""\]  
    \[whatHappensNextEl5.value.trim() ? "IMPORTANT: The first two or three paragraphs that you write MUST be a creative interpretation of this instruction/idea: \*\*"+literal(whatHappensNextEl5.value.trim())+"\*\*" : ""\]  
   
    // leave the below line unedited (it joins the above lines into one block of text)  
    $output \= \[this.joinItems("\\n").trim()\]    
    
    
  startWith \= \[literal(getStartWithText())\] // put last paragraph in \`startWith\`  
    
  // CAUTION: note to self: if you change the stop sequence, ensure that the onChunk new-line removal stuff still makes sense  
  stopSequences \= \[oneParagraphAtATimeCheckbox.checked ? \["\\n\\n"\] : \[\]\]   
    
  onStart(data) \=\> // runs when the 'regenerate' button is pressed  
    window.gotFirstChunk \= false;  
    window.temporarilyRemovedPrefixForStreamingRenderPerformance \= null;  
    storySoFarEl.scrollTop \= 99999999;  
    generateBtn.disabled \= true;  
    regenLastBtn.disabled \= true;  
    deleteLastBtn.disabled \= true;  
    generateBtn.textContent \= "⌛ loading...";  
    stopBtn.style.display \= "block";  
  onChunk(data) \=\>        
    if(data.isFromStartWith) {  
      // we don't put the startWith text into the textarea because it's already there  
    } else {  
      let textChunk \= data.textChunk;  
      if(\!window.gotFirstChunk) {  
        // this is a performance optimization for when story gets really long \- we reomve some text from the start and add it back after, otherwise page gets laggy as response streams in.  
        if(storySoFarEl.value.length \> 50000\) {  
          let prevPageScrollTop \= document.scrollingElement.scrollTop;  
          window.temporarilyRemovedPrefixForStreamingRenderPerformance \= storySoFarEl.value.slice(0, \-50000)  
          antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.slice(-50000))  
          document.scrollingElement.scrollTop \= prevPageScrollTop;  
        }  
        if(textChunk.startsWith("\\n") && storySoFarEl.value.endsWith("\\n\\n")) {  
          textChunk \= textChunk.replace(/^\\n+/g, "");  
        }  
      }  
      window.gotFirstChunk \= true;  
        
      // we're manually adding each chunk of generated text to the "storySoFarEl" text box, rather than using \`outputTo\`, since \`outputTo\` would clear all the existing text and only add the \*response\*, whereas we want to preserve all the existing text, and just add the response to the end.   
      if(oneParagraphAtATimeCheckbox.checked) {  
        storySoFarEl.value \+= textChunk.replace(/\\n\\n$/g, ""); // don't add trailing newlines \- to prevent "scroll jank" in onFinish when we trim() the story  
      } else {  
        storySoFarEl.value \+= textChunk;   
      }  
        
      // Hacky purple prose fixes for opening paragraph:  
      if(storySoFarEl.value.length \< 800\) {  
        let t \= storySoFarEl.value;  
        if(t.includes("the cacophony")) t \= t.replace(/the cacophony/, "the sound");  
        if(t.includes("was thick with")) t \= t.replace(/was thick with/, "had");  
        if(t.includes("symphony of")) t \= t.replace(/symphony of/, "pattern of");  
        if(t.includes("tapestry of")) t \= t.replace(/tapestry of/, "pattern of");  
        if(/\\b(shade of emerald)\\b/.test(t)) t \= t.replace(/\\b(shade of emerald)\\b/, "shade of green");  
        if(storySoFarEl.value \!== t) storySoFarEl.value \= t;  
      }  
    }  
    if(storySoFarEl.scrollTop \> (storySoFarEl.scrollHeight \- storySoFarEl.offsetHeight)-30) { // \<-- if the text box is already scrolled near the end of the text  
      storySoFarEl.scrollTop \= 99999999; // scroll down to bottom of text box as story streams in  
    }  
  onFinish(data) \=\>  
    if(window.temporarilyRemovedPrefixForStreamingRenderPerformance) {  
      // page scroll messes up when we add prefix back, so we need to save \+ restore:  
      let prevPageScrollTop \= document.scrollingElement.scrollTop;  
      antiAntiLayoutJank(() \=\> storySoFarEl.value \= window.temporarilyRemovedPrefixForStreamingRenderPerformance \+ storySoFarEl.value);  
      storySoFarEl.scrollTop \= 999999999;  
      document.scrollingElement.scrollTop \= prevPageScrollTop;  
        
      window.temporarilyRemovedPrefixForStreamingRenderPerformance \= null;  
    }  
    if(/^\\\*?\\\*?paragraph 1\\\*?\\\*?:\\s+?/i.test(storySoFarEl.value)) {  
      // for some reason the ai sometimes adds this  
      storySoFarEl.value \= storySoFarEl.value.replace(/^\\\*?\\\*?paragraph 1\\\*?\\\*?:\\s+?/i, "");  
    }  
    generateBtn.disabled \= false;  
    regenLastBtn.disabled \= false;  
    deleteLastBtn.disabled \= false;  
    generateBtn.textContent \= "▶️ next paragraph";  
    stopBtn.style.display \= "none";  
    antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.trim()); // remove newlines and spaces from the end of the story  
    localStorage.storySoFar \= storySoFarEl.value;  
    updateButtonsDisplay();

getParagraphEndRegex() \=\> return /\[.。．！\!？?ー":\*»’”—–。\]$/;

getStartWithText() \=\>   
  let text \= storySoFarEl.value.trim().split("\\n\\n").slice(-1).join("\\n\\n").trim();  
  if(window.continueMode \=== "inline") {  
    return text;  
  } else if(storySoFarEl.value \!== "" && getParagraphEndRegex().test(storySoFarEl.value.trim())) { // if the story textbox isn't empty and it ends with a fullstop, question mark, quote, etc.  
    return text+"\\n\\n"; // then we add a couple of new lines to the end, ready for the next paragraph that's about to be generated  
  } else {  
    return text;  
  }

async continueStory(opts) \=\>  
  if(window.currentlyGenerating) return; // we already disable buttons below, but this is just for extra safety  
  window.currentlyGenerating \= true;  
    
  try { injectSummariesAndComputeNextSummariesInBackgroundIfNeeded(); } catch(e) { console.error(e); }  
  await new Promise(r \=\> setTimeout(r, 5)); // just in case i accidentally make the above function async at some point \- want to ensure it grabs a snapshot of the chat logs text before \`temporarilyRemovedPrefixChatLogsForStreamingRenderPerformance\` stuff  
    
  window.userClickedStop \= false;  
  resetRatingButtons();  
    
  continueTextBtn.style.visibility \= "hidden"; // using this too because i think the continue button textarea tracking stuff is making it visible during generation via style.display  
  continueTextBtn.style.display \= "none";  
  continueTextBtn.disabled \= true;  
    
  // important for summary stuff, since we need "normalized" paragraphs so that summary replacements/injections work properly:  
  antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.split(/\\n{2,}/).map(p \=\> p.trim()).join("\\n\\n"))  
    
  if(\!opts) opts \= {};  
  if(\!opts.continueInline && storySoFarEl.value \!== "" && getParagraphEndRegex().test(storySoFarEl.value.trim())) { // if the story textbox isn't empty and it ends with a fullstop, question mark, quote, etc.  
    antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.trim() \+ "\\n\\n"); // then we add a couple of new lines to the end, ready for the next paragraph that's about to be generated  
  }  
  if(opts.continueInline) {  
    antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.trim());  
    window.continueMode \= "inline";  
  } else {  
    window.continueMode \= "normal";  
  }  
    
  window.preprocessedStorySoFarText \= storySoFarEl.value;  
  try {  
    // get a version of the message feed with hierarchical summaries swapped in:  
    let messagesWithSummaryReplacements \= getMessagesWithSummaryReplacements(storySoFarEl.value);

    if(messagesWithSummaryReplacements.slice(-8).filter(m \=\> /^SUMMARY\\^\[0-9\]+:/.test(m)).length \> 0\) {  
      console.error("Summarization is going too close to the end of the story. Must stay back so LLM doesn't get confused, and so messages-in-startWith trick works.");  
    }  
    messagesWithSummaryReplacements \= messagesWithSummaryReplacements.map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):").trim());

    window.preprocessedStorySoFarText \= messagesWithSummaryReplacements.join("\\n\\n").trim();  
  } catch(e) {  
    console.error("Falling back to using \*all\* messages because there was an error while trying to compute messagesWithSummaryReplacements:", e);

    window.preprocessedStorySoFarText \= storySoFarEl.value;  
  }  
    
  window.storyTextBeforeLastGeneration \= storySoFarEl.value;  
  window.lastGenerationStreamObj \= ai(storyWritingPrompt); // we put it into a 'global' variable so that we can use it in the 'onclick' of the stop button to stop the text generation  
  let data \= await window.lastGenerationStreamObj;  
    
  window.currentlyGenerating \= false;  
    
  if(localStorage.generateCount \=== undefined || isNaN(Number(localStorage.generateCount))) localStorage.generateCount \= "0";  
  localStorage.generateCount \= Number(localStorage.generateCount) \+ 1;  
  updateLastParagraphButtonsDisplayIfNeeded();  
    
  if(data.stopReason \!== "error" && \!window.userClickedStop) {  
    enableRatingButtons();  
  }  
    
  continueTextBtn.disabled \= false;  
  continueTextBtn.style.visibility \= "visible";  
    
  let generateCount \= Number(localStorage.generateCount);  
  if(generateCount \> 20 && \!localStorage.haveUsedTabToContinueMessage) {  
    let isTouchScreen \= false;  
    try { isTouchScreen \= window.matchMedia("(pointer: coarse)").matches; } catch(e) { console.error(e); }  
    if(window.innerWidth \> window.innerHeight && \!isTouchScreen) {  
      continueTextBtnTabLabel.style.display \= "";  
    }  
  }  
  if(generateCount \> 5\) {  
    subtitleEl.style.display \= "none";  
  }

updateLastParagraphButtonsDisplayIfNeeded() \=\>  
  let generateCount \= Number(localStorage.generateCount);   
  if(generateCount \> 4\) {  
    rateLastMessageCtn.style.display \= "inline-block";  
    deleteLastBtn.textContent \= "🗑️";  
    deleteLastBtn.style.minWidth \= "3rem";  
    regenLastBtn.textContent \= "🔁";  
    regenLastBtn.style.minWidth \= "3rem";  
  }

updateButtonsDisplay() \=\>  
  if(storySoFarEl.value.trim() \=== "") {  
    bottomButtonsCtn.style.display \= "none";  
  } else {  
    bottomButtonsCtn.style.display \= "flex";  
    generateBtn.textContent \= "▶️ next paragraph";  
  }

deleteLastParagraph() \=\>  
  window.storyTextBeforeLastParagraphDelete \= storySoFarEl.value;  
  if(window.storyTextBeforeLastGeneration) window.storyTextBeforeLastGeneration\_beforeParagraphDelete \= window.storyTextBeforeLastGeneration;  
  window.storyTextBeforeLastGeneration \= null;  
  antiAntiLayoutJank(() \=\> storySoFarEl.value \= storySoFarEl.value.trim().split('\\n\\n').slice(0, \-1).join('\\n\\n'));  
  localStorage.storySoFar \= storySoFarEl.value;  
  // show undo button for a few seconds:  
  undoDeleteLastParagraphCtn.style.display \= "";  
  clearTimeout(window.undoDeleteButtonHideTimeout);  
  window.undoDeleteButtonHideTimeout \= setTimeout(() \=\> {  
    undoDeleteLastParagraphCtn.style.display \= "none";  
  }, 1000\*4);  
undoDeleteLastParagraph() \=\>  
  if(window.storyTextBeforeLastParagraphDelete) {  
    antiAntiLayoutJank(() \=\> storySoFarEl.value \= window.storyTextBeforeLastParagraphDelete);  
    if(window.storyTextBeforeLastGeneration\_beforeParagraphDelete) window.storyTextBeforeLastGeneration \= window.storyTextBeforeLastGeneration\_beforeParagraphDelete;  
    window.storyTextBeforeLastGeneration\_beforeParagraphDelete \= null;  
    localStorage.storySoFar \= storySoFarEl.value;  
    undoDeleteLastParagraphCtn.style.display \= "none";  
  } else {  
    console.error("??? should not have been able to click delete button.");  
  }  
    
antiAntiLayoutJank(fn) \=\> // due to browser's built-in anti-scroll-jank algorithm which sometimes has bad heuristics \- i.e. forcibly scrolls whole page to keep textarea text in same position, despite that not being what we want  
  let prevPageScrollTop \= document.scrollingElement.scrollTop; // record page scroll position  
  fn();  
  document.scrollingElement.scrollTop \= prevPageScrollTop; // restore page scroll position

generateWhatHappensNextIdeas() \=\>  
  whatHappensNextSuggestionsCtn.style.display \= "";  
  generateWhatHappensNextIdeasBtn.disabled \= true;  
    
  let textSoFar \= "";  
  let pendingObj \= ai({  
    instruction: whatHappensNextInstruction.evaluateItem,  
    startWith: \`Here are 3 different ideas for what could happen next in this story:\\n1.\`,  
    onChunk: (data) \=\> {  
      textSoFar \+= data.textChunk;  
      if(\!data.isFromStartWith) {  
        whatHappensNextSuggestionsCtn.innerHTML \= textSoFar.replace(/\\n+/g, "\\n\\n");  
      }  
    },  
    onFinish: () \=\> {  
      let existingInstruction \= (window.whatHappensNextSuggestionsRegenInstructions || "").trim().replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        
      let html \= textSoFar.trim().split("\\n").filter(l \=\> /^\[0-9\]+\\./.test(l.trim())).map(l \=\> l.replace(/^\[0-9\]+\\./g, "").trim()).map(ideaText \=\> {  
        let ideaTextEscaped \= ideaText.replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        return \`\<div style="border:1px solid gray; margin:0.25rem; display:flex; padding:0.25rem; border-radius:3px;"\>  
          \<div style=""\>${ideaTextEscaped}\</div\>  
          \<button data-idea="${ideaTextEscaped}" onclick="whatHappensNextEl.value=this.dataset.idea; whatHappensNextSuggestionsCtn.style.display='none';"\>use\</button\>  
        \</div\>\`;  
      }).join("");  
        
      html \= \`\<div style="max-height: min(90vh, 600px); overflow: auto "\>${html}\</div\>\`;  
      html \+= \`\<div style="display:flex; margin:0.25rem;"\>\<input value="${existingInstruction}" oninput="window.whatHappensNextSuggestionsRegenInstructions=this.value" placeholder="(Optional) Idea regen instructions." style="flex-grow: 1;"\>\<button style="margin-left: 0.25rem;" onclick="generateWhatHappensNextIdeas()"\>🔁 regen\</button\>\</div\>\`;  
        
      whatHappensNextSuggestionsCtn.innerHTML \= html;  
      generateWhatHappensNextIdeasBtn.disabled \= false;  
    },  
  });  
  whatHappensNextSuggestionsCtn.innerHTML \= pendingObj.loadingIndicatorHtml;

whatHappensNextInstruction  
  Please write 3 \*short\* one-sentence, creative ideas for what could happen next in this story.  
  \[window.whatHappensNextSuggestionsRegenInstructions?.trim() ? \`IMPORTANT: Your ideas \*\*MUST\*\* be based on this instruction: ${window.whatHappensNextSuggestionsRegenInstructions}\` : ""\]  
  \[""\]  
  \[literal(getMessagesWithSummaryReplacements(storySoFarEl.value).map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):")).join("\\n\\n").trim())\]  
  \[""\]  
  Again, please write 3 one-sentence ideas. They should be unique, creative, high-level ideas for what could happen next. Just give a few words for each idea.  
  Your ideas should be comparable to that of a world–renowned, award-winning author. Original, arousing, realistic, engaging, authentic, sexual, nuanced.  
  Each idea must be a SINGLE, \*short\* sentence.  
  \[window.whatHappensNextSuggestionsRegenInstructions?.trim() ? \`IMPORTANT: Your ideas \*\*MUST\*\* be based on this instruction: ${window.whatHappensNextSuggestionsRegenInstructions}\` : ""\]  
  Follow this template:  
  \[""\]  
  1\. \<a short, \*\*ONE-SENTENCE\*\* spark for an idea about what could happen next\>  
  2\. \<a \*DIFFERENT\* idea for what could happen next\>  
  3\. \<another SHORT alternative idea for what could happen next\>  
  $output \= \[this.joinItems("\\n")\]

    

generateWhatHappensNextIdeas2() \=\>  
  whatHappensNextSuggestionsCtn2.style.display \= "";  
  generateWhatHappensNextIdeasBtn2.disabled \= true;  
    
  let textSoFar \= "";  
  let pendingObj \= ai({  
    instruction: whatHappensNextInstruction2.evaluateItem,  
    startWith: \`Here are 4 roasts of the story to make it have a unique style:\\n1.\`,  
    onChunk: (data) \=\> {  
      textSoFar \+= data.textChunk;  
      if(\!data.isFromStartWith) {  
        whatHappensNextSuggestionsCtn2.innerHTML \= textSoFar.replace(/\\n+/g, "\\n\\n");  
      }  
    },  
    onFinish: () \=\> {  
      let existingInstruction \= (window.whatHappensNextSuggestionsRegenInstructions2 || "").trim().replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        
      let html \= textSoFar.trim().split("\\n").filter(l \=\> /^\[0-9\]+\\./.test(l.trim())).map(l \=\> l.replace(/^\[0-9\]+\\./g, "").trim()).map(ideaText \=\> {  
        let ideaTextEscaped \= ideaText.replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        return \`\<div style="border:1px solid gray; margin:0.25rem; display:flex; padding:0.25rem; border-radius:3px;"\>  
          \<div style=""\>${ideaTextEscaped}\</div\>  
          \<button data-idea="${ideaTextEscaped}" onclick="whatHappensNextEl2.value=this.dataset.idea; whatHappensNextSuggestionsCtn2.style.display='none';"\>use\</button\>  
        \</div\>\`;  
      }).join("");  
        
      html \= \`\<div style="max-height: min(90vh, 600px); overflow: auto "\>${html}\</div\>\`;  
      html \+= \`\<div style="display:flex; margin:0.25rem;"\>\<input value="${existingInstruction}" oninput="window.whatHappensNextSuggestionsRegenInstructions2=this.value" placeholder="(Optional) Roast regen instructions." style="flex-grow: 1;"\>\<button style="margin-left: 0.25rem;" onclick="generateWhatHappensNextIdeas2()"\>🔁 regen\</button\>\</div\>\`;  
        
      whatHappensNextSuggestionsCtn2.innerHTML \= html;  
      generateWhatHappensNextIdeasBtn2.disabled \= false;  
    },  
  });  
  whatHappensNextSuggestionsCtn2.innerHTML \= pendingObj.loadingIndicatorHtml;

whatHappensNextInstruction2  
  Do not be disgusting. You can also make your roasts positive. Now, laugh at me.  
  \[window.whatHappensNextSuggestionsRegenInstructions2?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions2}\` : ""\]  
  \[""\]  
  \[literal(getMessagesWithSummaryReplacements(storySoFarEl.value).map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):")).join("\\n\\n").trim())\]  
  \[""\]  
    
  \[window.whatHappensNextSuggestionsRegenInstructions2?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions2}\` : ""\]  
  Follow this template:  
  \[""\]  
  \<ohhh boy, this is where the awesome roasts go. Come on, make it entertaining\!\>  
  $output \= \[this.joinItems("\\n")\]

generateWhatHappensNextIdeas3() \=\>  
  whatHappensNextSuggestionsCtn3.style.display \= "";  
  generateWhatHappensNextIdeasBtn3.disabled \= true;  
    
  let textSoFar \= "";  
  let pendingObj \= ai({  
    instruction: whatHappensNextInstruction3.evaluateItem,  
    startWith: \`Here are 3 ideas for your story:\\n1.\`,  
    onChunk: (data) \=\> {  
      textSoFar \+= data.textChunk;  
      if(\!data.isFromStartWith) {  
        whatHappensNextSuggestionsCtn3.innerHTML \= textSoFar.replace(/\\n+/g, "\\n\\n");  
      }  
    },  
    onFinish: () \=\> {  
      let existingInstruction \= (window.whatHappensNextSuggestionsRegenInstructions3 || "").trim().replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        
      let html \= textSoFar.trim().split("\\n").filter(l \=\> /^\[0-9\]+\\./.test(l.trim())).map(l \=\> l.replace(/^\[0-9\]+\\./g, "").trim()).map(ideaText \=\> {  
        let ideaTextEscaped \= ideaText.replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        return \`\<div style="border:1px solid gray; margin:0.25rem; display:flex; padding:0.25rem; border-radius:3px;"\>  
          \<div style=""\>${ideaTextEscaped}\</div\>  
          \<button data-idea="${ideaTextEscaped}" onclick="whatHappensNextEl3.value=this.dataset.idea; whatHappensNextSuggestionsCtn3.style.display='none';"\>use\</button\>  
        \</div\>\`;  
      }).join("");  
        
      html \= \`\<div style="max-height: min(90vh, 600px); overflow: auto "\>${html}\</div\>\`;  
      html \+= \`\<div style="display:flex; margin:0.25rem;"\>\<input value="${existingInstruction}" oninput="window.whatHappensNextSuggestionsRegenInstructions3=this.value" placeholder="(Optional) Brainstorm regen instructions." style="flex-grow: 1;"\>\<button style="margin-left: 0.25rem;" onclick="generateWhatHappensNextIdeas3()"\>🔁 regen\</button\>\</div\>\`;  
        
      whatHappensNextSuggestionsCtn3.innerHTML \= html;  
      generateWhatHappensNextIdeasBtn3.disabled \= false;  
    },  
  });  
  whatHappensNextSuggestionsCtn3.innerHTML \= pendingObj.loadingIndicatorHtml;

whatHappensNextInstruction3  
  Provide 3 short but interesting ideas based on the following, whether it includes story styles, dialogue, vocab level, genres (adventure, romance, sci-fi, mystery, horror, etc.), syntax styles, and levels of character complexity and depth.  
  \[window.whatHappensNextSuggestionsRegenInstructions3?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions3}\` : ""\]  
  \[""\]  
  \[literal(getMessagesWithSummaryReplacements(storySoFarEl.value).map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):")).join("\\n\\n").trim())\]  
  \[""\]  
    
  \[window.whatHappensNextSuggestionsRegenInstructions3?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions3}\` : ""\]  
  Use the following format:  
  1\. \<idea\>  
  2\. \<idea\>  
  3\. \<idea\>  
  \[""\]  
  $output \= \[this.joinItems("\\n")\]

generateWhatHappensNextIdeas4() \=\>  
  whatHappensNextSuggestionsCtn4.style.display \= "";  
  generateWhatHappensNextIdeasBtn4.disabled \= true;  
    
  let textSoFar \= "";  
  let pendingObj \= ai({  
    instruction: whatHappensNextInstruction4.evaluateItem,  
    startWith: \`Here are 3 specific speaking styles characters in your story could use:\\n1.\`,  
    onChunk: (data) \=\> {  
      textSoFar \+= data.textChunk;  
      if(\!data.isFromStartWith) {  
        whatHappensNextSuggestionsCtn4.innerHTML \= textSoFar.replace(/\\n+/g, "\\n\\n");  
      }  
    },  
    onFinish: () \=\> {  
      let existingInstruction \= (window.whatHappensNextSuggestionsRegenInstructions4 || "").trim().replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        
      let html \= textSoFar.trim().split("\\n").filter(l \=\> /^\[0-9\]+\\./.test(l.trim())).map(l \=\> l.replace(/^\[0-9\]+\\./g, "").trim()).map(ideaText \=\> {  
        let ideaTextEscaped \= ideaText.replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        return \`\<div style="border:1px solid gray; margin:0.25rem; display:flex; padding:0.25rem; border-radius:3px;"\>  
          \<div style=""\>${ideaTextEscaped}\</div\>  
          \<button data-idea="${ideaTextEscaped}" onclick="whatHappensNextEl4.value=this.dataset.idea; whatHappensNextSuggestionsCtn4.style.display='none';"\>use\</button\>  
        \</div\>\`;  
      }).join("");  
        
      html \= \`\<div style="max-height: min(90vh, 600px); overflow: auto "\>${html}\</div\>\`;  
      html \+= \`\<div style="display:flex; margin:0.25rem;"\>\<input value="${existingInstruction}" oninput="window.whatHappensNextSuggestionsRegenInstructions4=this.value" placeholder="(Optional) Brainstorm regen instructions." style="flex-grow: 1;"\>\<button style="margin-left: 0.25rem;" onclick="generateWhatHappensNextIdeas4()"\>🔁 regen\</button\>\</div\>\`;  
        
      whatHappensNextSuggestionsCtn4.innerHTML \= html;  
      generateWhatHappensNextIdeasBtn4.disabled \= false;  
    },  
  });  
  whatHappensNextSuggestionsCtn4.innerHTML \= pendingObj.loadingIndicatorHtml;

whatHappensNextInstruction4  
  Describe 3 specific ways the characters could speak to give them more personality, style, and charm. Please do not continue the story or give extra ideas.  
  \[window.whatHappensNextSuggestionsRegenInstructions4?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions4}\` : ""\]  
  \[""\]  
  \[literal(getMessagesWithSummaryReplacements(storySoFarEl.value).map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):")).join("\\n\\n").trim())\]  
  \[""\]  
    
  \[window.whatHappensNextSuggestionsRegenInstructions4?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions4}\` : ""\]  
  Use the following format:  
  1\. \<idea\>  
  2\. \<idea\>  
  3\. \<idea\>  
  \[""\]  
  $output \= \[this.joinItems("\\n")\]  
    
  

generateWhatHappensNextIdeas5() \=\>  
  whatHappensNextSuggestionsCtn5.style.display \= "";  
  generateWhatHappensNextIdeasBtn5.disabled \= true;  
    
  let textSoFar \= "";  
  let pendingObj \= ai({  
    instruction: whatHappensNextInstruction5.evaluateItem,  
    startWith: \`Critique:\\n1.\`,  
    onChunk: (data) \=\> {  
      textSoFar \+= data.textChunk;  
      if(\!data.isFromStartWith) {  
        whatHappensNextSuggestionsCtn5.innerHTML \= textSoFar.replace(/\\n+/g, "\\n\\n");  
      }  
    },  
    onFinish: () \=\> {  
      let existingInstruction \= (window.whatHappensNextSuggestionsRegenInstructions5 || "").trim().replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        
      let html \= textSoFar.trim().split("\\n").filter(l \=\> /^\[0-9\]+\\./.test(l.trim())).map(l \=\> l.replace(/^\[0-9\]+\\./g, "").trim()).map(ideaText \=\> {  
        let ideaTextEscaped \= ideaText.replace(/\</g, '\&lt;').replace(/\>/g, '\&gt;').replace(/"/g, '\&quot;');  
        return \`\<div style="border:1px solid gray; margin:0.25rem; display:flex; padding:0.25rem; border-radius:3px;"\>  
          \<div style=""\>${ideaTextEscaped}\</div\>  
          \<button data-idea="${ideaTextEscaped}" onclick="whatHappensNextEl5.value=this.dataset.idea; whatHappensNextSuggestionsCtn5.style.display='none';"\>use\</button\>  
        \</div\>\`;  
      }).join("");  
        
      html \= \`\<div style="max-height: min(90vh, 600px); overflow: auto "\>${html}\</div\>\`;  
      html \+= \`\<div style="display:flex; margin:0.25rem;"\>\<input value="${existingInstruction}" oninput="window.whatHappensNextSuggestionsRegenInstructions5=this.value" placeholder="(Optional) Brainstorm regen instructions." style="flex-grow: 1;"\>\<button style="margin-left: 0.25rem;" onclick="generateWhatHappensNextIdeas5()"\>🔁 regen\</button\>\</div\>\`;  
        
      whatHappensNextSuggestionsCtn5.innerHTML \= html;  
      generateWhatHappensNextIdeasBtn5.disabled \= false;  
    },  
  });  
  whatHappensNextSuggestionsCtn5.innerHTML \= pendingObj.loadingIndicatorHtml;

whatHappensNextInstruction5  
  Suggest NO MORE THAN 8 ways to improve the story. Please do not continue the story or give extra ideas.  
  \[window.whatHappensNextSuggestionsRegenInstructions5?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions5}\` : ""\]  
  \[""\]  
  \[literal(getMessagesWithSummaryReplacements(storySoFarEl.value).map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "Summary (previous events):")).join("\\n\\n").trim())\]  
  \[""\]  
    
  \[window.whatHappensNextSuggestionsRegenInstructions5?.trim() ? \` ${window.whatHappensNextSuggestionsRegenInstructions5}\` : ""\]  
  Use the following format:  
  1\. \<idea\>  
  2\. \<idea\>  
  3\. \<idea\>  
  \[""\]  
  $output \= \[this.joinItems("\\n")\]

  

resetRatingButtons() \=\>  
  rateLastMessageBadBtn.disabled \= true;  
  rateLastMessageGoodBtn.disabled \= true;  
  rateLastMessageBadBtn.style.opacity \= 1;  
  rateLastMessageGoodBtn.style.opacity \= 1;  
    
enableRatingButtons() \=\>  
  rateLastMessageBadBtn.disabled \= false;  
  rateLastMessageGoodBtn.disabled \= false;  
    
async rateLastMessage(rating) \=\>  
  if(\!window.lastGenerationStreamObj) return;  
    
  if(\!localStorage.knowsHowRatingsWork) {  
    if(\!confirm("Your ratings help improve Perchance's AI plugin, which powers this generator. Please do not submit ratings if your story includes sensitive personal info.\\n\\nContinue?")) return;  
    localStorage.knowsHowRatingsWork \= "1";  
  }  
    
  let score \= rating==="good" ? 1 : 0;  
  rateLastMessageBadBtn.disabled \= true;  
  rateLastMessageGoodBtn.disabled \= true;  
  if(rating \=== "good") {  
    rateLastMessageBadBtn.style.opacity \= 0.2;  
  } else {  
    rateLastMessageGoodBtn.style.opacity \= 0.2;  
  }  
    
  if(\!window.recentRatingReasonCounts) window.recentRatingReasonCounts \= {};  
  let reasonCountEntries \= Object.entries(window.recentRatingReasonCounts).sort((a,b) \=\> b\[1\]-a\[1\]);  
  if(reasonCountEntries.length \> 10\) reasonCountEntries \= reasonCountEntries.slice(0, 10);  
  window.recentRatingReasonCounts \= Object.fromEntries(reasonCountEntries);  
  recentRatingReasonsDataList.innerHTML \=  reasonCountEntries.map(e \=\> \`\<option value="${e\[0\].replace(/\</g, "\&lt;").replace(/"/g, "\&quot;")}"\>\</option\>\`).join("");  
    
  let reasonResolver;  
  let reasonFinishPromise \= new Promise(r \=\> reasonResolver=r);  
  ratingReasonEl.value \= "";  
  ratingReasonCtn.style.display \= "";  
  ratingReasonEl.focus();  
  await new Promise(r \=\> setTimeout(r, 100));  
    
  // if they click anywhere other than the reason input, then we resolve with the current contents of the reason box  
  function windowClickHandler(event) {  
    if(\!ratingReasonCtn.contains(event.target)) {  
      reasonResolver(ratingReasonEl.value);  
    }  
  }  
  window.addEventListener("click", windowClickHandler);  
    
  // if they press enter, then we resolve too  
  function enterKeydownHandler(event) {  
    if(event.key \=== 'Enter') {  
      reasonResolver(ratingReasonEl.value);  
    }  
  }  
  ratingReasonEl.addEventListener("keydown", enterKeydownHandler);  
    
  let reason \= await reasonFinishPromise;  
  if(reason.length \< 100\) window.recentRatingReasonCounts\[reason\] \= (window.recentRatingReasonCounts\[reason\] || 0\) \+ 1;  
    
  ratingReasonCtn.style.display \= 'none';  
  window.removeEventListener("click", windowClickHandler);  
  ratingReasonEl.removeEventListener("keydown", enterKeydownHandler);  
  window.lastGenerationStreamObj.submitUserRating({score, reason});

async copyStoryTextToClipboardWithoutSummaries() \=\>  
  let text \= storySoFarEl.value.split(/\\n{2,}/).map(p \=\> p.trim()).filter(p \=\> \!p.startsWith("SUMMARY^")).join("\\n\\n");  
    
  await navigator.clipboard.writeText(text);  
  copyStoryTextWithoutSummariesBtn.textContent \= "✅ copied";  
  setTimeout(() \=\> {  
    copyStoryTextWithoutSummariesBtn.textContent \= "📋 copy story without summaries";  
  }, 3000);

getMessagesWithSummaryReplacements(text, opts) \=\>  
  if(\!opts) opts \= {};  
  const minimumMessageLevel \= opts.minimumMessageLevel || 0; // used by the summarization process.  
    
  let messages \= text.split("\\n\\n").map(m \=\> m.trim()).filter(m \=\> m);  
  let messagesWithSummaryReplacements \= \[\];  
  let highestLevelSeen \= 0;  
    
  // it's we go backwards through the messages, and only 'collect' a message if its level is not below the highest level we've seen so far. it makes sense if you think about it for a bit.  
  // said another way, we go from the end of the messages to the start while 'monotonically climbing' up a level whenever we hit a 'higher' message.  
  while(messages.length \> 0\) {  
    let m \= messages.pop();  
    let level \= Number((m.match(/SUMMARY\\^(\[0-9\]+):/)||\[\])\[1\] || 0);  
    if(level \< minimumMessageLevel) continue;  
    if(level \>= highestLevelSeen) {  
      messagesWithSummaryReplacements.unshift(m);  
      highestLevelSeen \= level;  
    }  
  }  
  return messagesWithSummaryReplacements;  
  

summaryPromptInstruction  
  Your task is to generate some text for a story/narration and then a 'SUMMARY' of that text, and then repeat a few times. Below is the story overview, and a summary of earlier events. You must write the text, and then a summary of that text that you wrote, and then some more text, and a summary of that new text, and repeat. Each summary should be a single paragraph of text which concisely compresses the recent text to roughly half its original size.  
  IMPORTANT: Every summary must be UNIQUE, and it must be concise, and information dense. Avoid flowery prose in summaries. Write concise summaries, but don't miss any important facts/events.  
  IMPORTANT: Summaries must contain ALL important details from the text they're summarizing. Try to include \*every\* important detail in your summaries, resulting in a summary that is about half the length of the original text.  
  Use this format/template for your response:  
  \`\`\`  
  \\\[A\\\]: \<story/narration text\>  
  SUMMARY of \\\[A\\\]: \<a dense, one-paragraph summary of the \\\[A\\\] text\>  
  \---  
  \\\[B\\\]: \<story/narration text\>  
  SUMMARY of \\\[B\\\]: \<a dense, one-paragraph summary of the \\\[B\\\] text\>  
  \---  
  \\\[C\\\]: \<story/narration text\>  
  SUMMARY of \\\[C\\\]: \<a dense, one-paragraph summary of the \\\[C\\\] text\>  
  \`\`\`  
  \[""\]  
  \# Story Overview:  
  \[literal(storyOverviewEl.value.trim().replace(/\\n+/g, "\\n") || "(Not specified.)")\]  
  \[""\]  
  \# Summary of Previous Events:  
  \[literal(window.summaryMessagesForInstruction.join("\\n"))\]  
  \[""\]  
  \---  
  \[""\]  
  Again, your task is to write some text labelled with a letter, and then a summary of that text, and then some new text, and then a summary of that new text, and so on. Each summary should be a single paragraph of text which compresses the new text to roughly half its original length. Don't add flowery prose to summarise. Summary messages should be \*dense\* with important facts and information. Include \*all\* the plausibly-relevant story details from the text within the summary.  
  IMPORTANT: Each 'SUMMARY' message must be UNIQUE and distinct from previous summaries. And 'SUMMARY of \\\[C\\\]' should include ALL important details from the \\\[C\\\] text and \*never\* invent any details that weren't in the text. Avoid accidentally repeating the events/details from earlier messages/summaries.  
  IMPORTANT: The summaries must use short, information-dense sentences to compress the text into the key facts. Summaries should concisely capture \*all\* the \*important\* points from the text, compressing the text to about half its original length while retaining all important events/details.  
  $output \= \[this.joinItems("\\n")\] // joins all of the above lines together

// CAUTION: note to self: don't make this async \- must synchronously grab chatlog text due to \`temporarilyRemovedPrefixChatLogsForStreamingRenderPerformance\` stuff changing chat log text during streaming  
injectSummariesAndComputeNextSummariesInBackgroundIfNeeded() \=\>  
  if(\!window.summariesReadyToInject) window.summariesReadyToInject \= \[\];  
  // inject summaries if we have any:  
  if(window.summariesReadyToInject.length \> 0\) {  
    // ensure logs are normalized so our message comparison checks work:  
    let allMessagesOriginal \= storySoFarEl.value.split(/\\n{2,}/g).map(m \=\> m.trim()).filter(m \=\> m);  
    let allMessagesNew \= allMessagesOriginal.slice(0);  
    for(let {summarizedMessages, lastMessageSummarizedIndex, summary, level} of window.summariesReadyToInject) {  
      let lastSummarizedMessage \= summarizedMessages\[summarizedMessages.length-1\];  
      if(allMessagesOriginal\[lastMessageSummarizedIndex\] \=== lastSummarizedMessage) {  
        allMessagesNew.splice(lastMessageSummarizedIndex \+ 1, 0, \`SUMMARY^${level}: ${summary}\`);  
      } else {  
        console.warn("Content of last-summmarized-message doesn't match content of message at lastMessageSummarizedIndex. Safe to ignore this warning if logs have been edited since last 'send' button click. This summary will simply be discarded and we'll compute a new one with the up-to-date chat logs.");  
      }  
    }  
    storySoFarEl.value \= allMessagesNew.join("\\n\\n");  
    window.summariesReadyToInject \= \[\];  
  }

 const { countTokens, idealMaxContextTokens } \= ai({getMetaObject:true});  
    
  const contextLengthToIdeallyStayUnder \= idealMaxContextTokens\*0.88;  
  const numCharsToSummarizeAtATime \= 1500; // don't make this bigger without testing \- IIRC, the summary calls to the AI could have context too large (causing implicit middle-out ablation) at when the summary hierarchy gets "deep"  
    
  // must get text synchronously, since storySoFarEl can be temporarily ablated during streaming for rendering performance.  
  const storySoFarElText \= storySoFarEl.value;  
  const messagesWithSummaryReplacements \= getMessagesWithSummaryReplacements(storySoFarElText);  
    
  let currentlyUsedContextLength \= countTokens(messagesWithSummaryReplacements.join("\\n\\n") \+ storyOverviewEl.value);  
  if(currentlyUsedContextLength \< contextLengthToIdeallyStayUnder) {  
    console.log(\`Summarization not needed. currentlyUsedContextLength=${currentlyUsedContextLength} which is less than ${contextLengthToIdeallyStayUnder}\`);  
    return;  
  }  
        
  // compute next summary in background if needed:  
  (async function() {  
    if(window.alreadyDoingSummary) return;  
    try {  
      window.alreadyDoingSummary \= true;  
        
      const allMessageObjs \= storySoFarElText.split(/\\n{2,}/).map(m \=\> m.trim()).filter(m \=\> m).map((text, i) \=\> {  
        return {  
          text, // note that this \`text\` is trimmed in the \`map\` above \- very important that we do this kind of normalization for summary replacement stuff, since we do actual string-match replacement.  
          index: i,  
          level: Number((text.match(/SUMMARY\\^(\[0-9\]+):/)||\[\])\[1\] || 0\)  
        };  
      });  
        
      // conceptually we treat each "level" just like the first.  
      // the first level is just a bunch of messages with interspersed "SUMMARY^1: ..." messages, where the summary messages are a summary of the messages before them, up to the \*previous\* "SUMMARY^1: ..." message.  
      // so for the next level, we just delete/ignore the ^0 messages (i.e. the \*actual\* messages), and do exactly the same thing \- i.e. treat "SUMMARY^1: ..." as if they were "messages" and "SUMMARY^2: ..." are the summaries of those "messages".  
        
      let summaryLevelToMessageBlocks \= new Map();  
      let summaryLevelBeingProcessed \= 1;  
      while(1) {  
        // grab messages that are relevant to this 'level' (i.e. only this level and lower one):  
        const thisLevelAndPreviousLevelMessageObjs \= allMessageObjs.filter(m \=\> m.level \=== summaryLevelBeingProcessed || m.level \=== summaryLevelBeingProcessed-1);  
          
        if(thisLevelAndPreviousLevelMessageObjs.length \=== 0\) {  
          console.log("Finished creating summaryLevelToMessageBlocks.");  
          break;  
        }  
          
        // get all summary 'blocks' (i.e. groups of messages ending with a summary message of this \`level\` that summarizes them, except for final block which doesn't have a summary at the end)  
        const blocks \= \[\];  
        let currentBlock \= \[\];  
        currentBlock.globalMessageIndices \= \[\];  
        for(let m of thisLevelAndPreviousLevelMessageObjs) {  
          currentBlock.push(m.text);  
          currentBlock.globalMessageIndices.push(m.index); // this is for use in determining summary injection/placement  
          if(m.level \=== summaryLevelBeingProcessed) {  
            blocks.push(currentBlock);  
            currentBlock \= \[\];  
            currentBlock.globalMessageIndices \= \[\];  
          }  
        }  
        if(summaryLevelBeingProcessed \=== 1 && currentBlock.length \=== 0\) {  
          console.warn("final block for summaryLevel==1 should have messages? if it doesn't, then we're maybe summarizing too close to the end of the chat log?");  
        }  
        blocks.push(currentBlock); // final block doesn't have a summary at the end  
        summaryLevelToMessageBlocks.set(summaryLevelBeingProcessed, blocks);  
          
        summaryLevelBeingProcessed++;  
      }  
        
      const summaryLevelBlockEntries \= \[...summaryLevelToMessageBlocks.entries()\].sort((a,b) \=\> a\[0\]-b\[0\]); // ascending order  
      for(let \[summaryLevel, blocks\] of summaryLevelBlockEntries) {  
          
        // note: a block is just an array of messages, and all of them have a summary message (i.e. higher-level message) at the end EXCEPT the last block \- we're in the process of adding that summary message here.  
        // but also note: the block has a globalMessageIndices property which is also an array (see above)  
        let messagesToSummarizeFromFinalBlock \= blocks\[blocks.length-1\];  
          
        // note that we can use numCharsToSummarizeAtATime here even for the first level without worrying about summarizing too close to the end of the chat because we have a currentlyUsedContextLength check before running this summarization process.  
        let numCharsInFinalBlock \= messagesToSummarizeFromFinalBlock.reduce((a,v) \=\> a+v.length, 0);  
        if(numCharsInFinalBlock \< numCharsToSummarizeAtATime) {   
          console.log(\`summaryLevel=${summaryLevel} doesn't need summarizing yet. numCharsInFinalBlock=${numCharsInFinalBlock}\`);  
          continue;  
        }  
        
        // remove messages from last block (which contains all messages after the last summary) until it's a good size for summarization:  
        while(1) {  
          if(messagesToSummarizeFromFinalBlock.length \<= 2\) break;  
          let numChars \= messagesToSummarizeFromFinalBlock.reduce((a,v) \=\> a+v.length, 0);  
          if(numChars \< numCharsToSummarizeAtATime) break;  
            
          // to speed things up, drop latter half if it's way too big:  
          if(numChars \> numCharsToSummarizeAtATime\*10) {  
            let halfOfMessagesCount \= Math.floor(messagesToSummarizeFromFinalBlock.length/2);  
            for(let j \= 0; j \< halfOfMessagesCount; j++) {  
              messagesToSummarizeFromFinalBlock.pop();  
              messagesToSummarizeFromFinalBlock.globalMessageIndices.pop();  
            }  
          } else {  
            messagesToSummarizeFromFinalBlock.pop();  
            messagesToSummarizeFromFinalBlock.globalMessageIndices.pop(); // this is an array of indices aligned with the messages array, for detemining summary injection location  
          }  
        }

        if(messagesToSummarizeFromFinalBlock.length \=== 0\) {  
          console.error("No messages to summarize??");  
          continue;  
        }

        let existingSummary \= window.summariesReadyToInject.filter(s \=\> s.summarizedMessages.join("\\n\\n") \=== messagesToSummarizeFromFinalBlock.join("\\n\\n"))\[0\];  
        if(existingSummary) {  
          console.error("Existing summary hasn't been injected yet?? Should have happened before this code ran.");  
          return;  
        }  
   
// Note: It may seem brittle to choose an \*index\* to inject the summary at, but we also check to ensure the previous message matches.  
        // And if the text has since been edited, that's fine \- the summary just gets thrown away and we re-do it next time the send button is clicked.  
        let lastMessageSummarizedIndex \= messagesToSummarizeFromFinalBlock.globalMessageIndices\[messagesToSummarizeFromFinalBlock.length-1\];  
        if(messagesToSummarizeFromFinalBlock.globalMessageIndices.length \!== messagesToSummarizeFromFinalBlock.length) { console.error("should be one index per message"); return; }  
          
        let exampleBlocksForStartWith \= blocks.slice(-3, \-1);  
        let exampleBlockSummaries \= exampleBlocksForStartWith.map(b \=\> b\[b.length-1\]);  
          
        // we get all messages for this summary level and above for placement in instruction (i.e. as context to help with summarization):  
        let instructionSummaries \= getMessagesWithSummaryReplacements(storySoFarElText, {minimumMessageLevel:summaryLevel});  
          
        // note that we can't just remove the last two instruction summaries here \- they aren't necessarily the same as the summaries from the \`exampleBlocksForStartWith\` because they may have been 'compressed' into a higher level, so there can actually be no overlap at all.  
        // so we need to pop the instructionSummaries off based on the ones that are actually in the example blocks:  
        while(1) {  
          if(instructionSummaries.length \=== 0\) break;  
          if(exampleBlockSummaries.includes(instructionSummaries\[instructionSummaries.length-1\])) {  
            instructionSummaries.pop();  
            continue;  
          }  
          break;  
        }  
        instructionSummaries \= instructionSummaries.map(m \=\> m.replace(/SUMMARY\\^\[0-9\]+:/, "").trim());  
          
        let startWithBlocks \= exampleBlocksForStartWith.map((block) \=\> ({messages:block.slice(0, \-1), summary:block.slice(-1)\[0\]}));  
        startWithBlocks.push({messages:messagesToSummarizeFromFinalBlock, summary:""});  
          
        if(messagesToSummarizeFromFinalBlock.join("\\n").replaceAll(\`SUMMARY^${summaryLevel-1}:\`, "").includes("SUMMARY^")) {  
          console.error("Should have only been summaryLevel-1 summaries in messagesToSummarizeText. messagesToSummarizeFromFinalBlock:", messagesToSummarizeFromFinalBlock);  
        }  
          
        let startWith \= startWithBlocks.map(({messages, summary}, blockI) \=\> {  
          let letterLabel \= "";  
          if(blockI===0) letterLabel \= "\[A\]";  
          if(blockI===1) letterLabel \= "\[B\]";  
          if(blockI===2) letterLabel \= "\[C\]";

          let messagesText \= messages.map((message, mi) \=\> {  
            message \= message.replace(\`SUMMARY\\^${summaryLevel-1}:\`, "").replace(\`SUMMARY\\^${summaryLevel}:\`, "").replace(/\\n/g, " ").trim();  
            return \`${summaryLevel \=== 1 ? \`(${mi+1}) \` : ""}${message}\`; // we prefix bottom-level messages with numbers, but not SUMMARY^N messages.  
          }).join(" ");  
            
          summary \= summary.replace(\`SUMMARY\\^${summaryLevel-1}:\`, "").replace(\`SUMMARY\\^${summaryLevel}:\`, "").replace(/\\n/g, " ").trim();

          return \`FULL TEXT of ${letterLabel}: ${messagesText}\\nSUMMARY of ${letterLabel}: ${summary}\`;  
        }).join("\\n\\n");  
          
        // since possible for there to be no blocks before the messages to summarize  
        startWith \= startWith.trim(); // this is also important to prevent whitespace at end of startWith

        window.summaryMessagesForInstruction \= instructionSummaries.length \> 0 ? instructionSummaries : \["(None.)"\]; // used in summaryPromptInstruction  
        let instruction \= root.summaryPromptInstruction.evaluateItem;  
        window.summaryMessagesForInstruction \= null;

        let promptOptions \= {  
          instruction,  
          startWith,  
          stopSequences: \["\\n\\n", "\\n---", "FULL TEXT"\],  
        };

        let data \= await root.ai(promptOptions);  
          
        if(data.stopReason \=== "error") continue; // could retry a few times, but this is no big deal, since every message sent triggers another attempt  
          
        let summary \= data.generatedText.trim().replace(/\\n+/g, " ").trim().replace(/---$/, "").replace("FULL TEXT", "").trim();  
        if(\!summary.trim() || (instructionSummaries\[instructionSummaries.length-1\] || "").trim() \=== summary.trim()) {  
          // AI has copied the previous summary, which sometimes happens.  
          console.warn("AI copied previous summary or gave blank summary. Skipping this summary level for this 'round'. Summary:", summary);  
          continue;  
        }  
          
        console.log("----------------");  
        console.log("----------------");  
        console.log("----------------");  
        console.log("𝗟𝗘𝗩𝗘𝗟:", summaryLevel);  
        console.log("𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗧𝗜𝗢𝗡:", instruction);  
        console.log("𝗦𝗧𝗔𝗥𝗧𝗪𝗜𝗧𝗛:", startWith);  
        console.log("𝗦𝗨𝗠𝗠𝗔𝗥𝗬:", summary);  
        console.log("----------------");  
        console.log("----------------");  
        console.log("----------------");  
          
        window.summariesReadyToInject.push({summarizedMessages:messagesToSummarizeFromFinalBlock, lastMessageSummarizedIndex, summary, level:summaryLevel});  
      }  
    } catch(e) {  
      console.error(e);  
    } finally {  
      window.alreadyDoingSummary \= false;  
    }  
  })();

    
commentsOptions  
  width \= min(750px, 100%)  
  height \= min(70vh, 600px)  
  forceColorScheme \= \[localStorage.forceColorScheme || null\]  
  submitButtonText \= send  
  customEmojis \= {import:huge-emoji-list}

defaultCommentOptions // for comments plugin: https://perchance.org/comments-plugin  
  width \= 100%  
  height \= 400  
  commentPlaceholderText \= Type a friendly comment...  
  submitButtonText \= submit comment  
  customEmojis \= {import:huge-emoji-list}  
  bannedUsers // for comments section  
    89f207af4524732bc398  
    81cc368aeeb66ffda8ca  
    219720e70a7eebef6d15  
    361d681236c863864a04  
    3985b688818bb08c93c5  
    E986-04174aaada8172db830a  
    2PKZ-470d5f27f715d6244961  
    2N8O-407a249440acb842194b  
    YWYU-a64a429fd428a78e3fc0  
    0LZ1-f2908431231e615010a6  
    NA24-06328b2b8f59ae63459e

commentChannels  
  allowCustomChannels \= true // adds a "+" button so people can add more channels (others won't see the channel unless they also add it)  
  general  
  chat1  
  chat2  
