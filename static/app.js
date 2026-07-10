
// Export chat
function exportChat(){
  var ms = msgs.querySelectorAll('.msg');
  if(ms.length === 0){ alert('No chat to export.'); return; }
  var text = 'VerdeBuddy Chat Export\n' + new Date().toLocaleString() + '\n\n';
  ms.forEach(function(m){
    var bbl = m.querySelector('.bbl');
    if(!bbl) return;
    var who = m.classList.contains('u') ? 'Farmer' : 'VerdeBuddy';
    text += who + ': ' + bbl.textContent + '\n\n';
  });
  var a = document.createElement('a');
  a.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(text);
  a.download = 'verdebuddy-chat-' + Date.now() + '.txt';
  a.click();
}


// Language toggle
var activeLang = 'en';
var lastQuestion = '';
function setLang(lang){
  activeLang = lang;
  document.querySelectorAll('.lang-btn').forEach(function(b){
    b.style.background = b.dataset.lang === lang ? 'rgba(233, 220, 220, 0.658)' : 'rgba(12,50,8,0.7)';
  });
}

// Voice input
function startVoice(){
  if(!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)){
    alert('Voice input not supported in this browser.');
    return;
  }
  var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  var r = new SR();
  var langMap = {en:'en-NG', ha:'ha-NG'};
  r.lang = langMap[activeLang] || 'en-NG', 'ha-NG';
  r.interimResults = false;
  r.maxAlternatives = 1;
  var micBtn = document.getElementById('mic-btn');
  if(micBtn) micBtn.style.border = '2px solid #ff6b6b';
  r.onresult = function(e){
    inp.value = e.results[0][0].transcript;
    if(micBtn) micBtn.style.border = '1px solid #4CAF50';
    doSend();
  };
  r.onerror = function(){ if(micBtn) micBtn.style.border = '1px solid #4CAF50'; };
  r.onend = function(){ if(micBtn) micBtn.style.border = '1px solid #4CAF50'; };
  r.start();
}

// Suggested follow-ups
var topicFollowups = {
  en: {
    crop:      ["What fertilizer should I use?", "What is the ROI on this crop?", "When is the best time to sell?"],
    soil:      ["How do I test my soil pH?", "What fertilizer fixes this soil issue?", "Which crops suit this soil type?"],
    weather:   ["When should I plant based on this?", "What are the flood/drought risks here?", "Which crops handle this climate best?"],
    market:    ["Which market sells this for the best price?", "When is the best time to sell?", "How do I add value before selling?"],
    invest:    ["Which states are best for investment?", "What are the export opportunities?", "What is the ROI on this crop?"],
    disease:   ["How do I prevent this from spreading?", "What pesticide should I use?", "Is this disease common in my state?"],
    default:   ["What fertilizer should I use?", "When is the best time to sell?", "Which states are best for investment?"]
  },
  ha: {
    crop:      ["Wane taki zan yi amfani?", "Yaushe lokacin siyarwa?", "Yaya zan magance wannan cuta?"],
    soil:      ["Ta yaya zan gwada kasa ta?", "Wane taki ya dace da wannan kasa?", "Wadanne amfanin gona suka dace da wannan kasa?"],
    weather:   ["Yaushe zan shuka bisa ga wannan yanayi?", "Akwai hadarin ambaliya ko fari?", "Wadanne amfanin gona suka dace da wannan yanayi?"],
    market:    ["Wace kasuwa ce ta fi kyawun farashi?", "Yaushe lokacin siyarwa?", "Ta yaya zan kara darajar kayana kafin sayarwa?"],
    invest:    ["Wadanne jihohi suka fi kyau don zuba jari?", "Akwai damar fitarwa zuwa kasashen waje?", "Menene ribar wannan amfanin gona?"],
    disease:   ["Ta yaya zan hana yaduwar wannan cuta?", "Wane maganin kwari zan yi amfani?", "Wannan cuta ta zama ruwan dare a jihata?"],
    default:   ["Wane taki zan yi amfani?", "Yaushe lokacin siyarwa?", "Wadanne jihohi suka fi kyau don zuba jari?"]
  }
};

function detectTopic(text){
  var t = text.toLowerCase();
  if (/roi|invest|return|profit|export|zuba jari|riba/.test(t)) return "invest";
  if (/disease|pest|cuta|kwari|blight|rot|virus/.test(t)) return "disease";
  if (/soil|ph|kasa|fertilizer/.test(t)) return "soil";
  if (/rain|weather|season|damina|rani|yanayi|flood|drought/.test(t)) return "weather";
  if (/market|price|sell|kasuwa|farashi|siyarwa/.test(t)) return "market";
  return "crop";
}

function showFollowups(answer){
  var existing = document.getElementById('followup-bar');
  if(existing) existing.remove();

  // Generate contextual follow-ups based on answer content
  var a = answer.toLowerCase();
  var suggestions = [];

  // Crop-specific follow-ups
  if(a.includes('maize') || a.includes('corn') || a.includes('masara')){
    suggestions = ['What fertilizer does maize need?','When should I harvest maize?','What diseases affect maize?','Best maize variety for Kano?'];
  } else if(a.includes('tomato')){
    suggestions = ['How do I prevent tomato blight?','When is the best time to sell tomatoes?','What fertilizer for tomatoes?','How to grow tomatoes in dry season?'];
  } else if(a.includes('cassava')){
    suggestions = ['How do I process cassava into garri?','What is the market price for cassava?','Best cassava variety for high yield?','How to store cassava after harvest?'];
  } else if(a.includes('rice')){
    suggestions = ['What fertilizer does rice need?','How much water does rice need?','Best rice variety for Nigeria?','When to harvest rice?'];
  } else if(a.includes('yam')){
    suggestions = ['How to store yam after harvest?','What is the best time to plant yam?','What fertilizer for yam?','How to control yam beetle?'];
  } else if(a.includes('groundnut') || a.includes('peanut')){
    suggestions = ['How to prevent groundnut rosette disease?','When is the best time to sell groundnut?','How to store groundnut safely?','What is groundnut export price?'];
  } else if(a.includes('soybean') || a.includes('soya')){
    suggestions = ['Where can I sell soybean?','What fertilizer does soybean need?','When to harvest soybean?','What is soybean market price?'];
  } else if(a.includes('pepper')){
    suggestions = ['How to dry pepper for storage?','What is pepper market price?','How to prevent pepper blight?','When to harvest pepper?'];
  } else if(a.includes('onion')){
    suggestions = ['How to cure onion for storage?','When is the best time to sell onion?','What fertilizer for onion?','How to prevent onion downy mildew?'];
  } else if(a.includes('ginger')){
    suggestions = ['How to export ginger from Nigeria?','What is ginger export price?','How to dry ginger for export?','Where to sell ginger in Nigeria?'];
  } else if(a.includes('sesame') || a.includes('benniseed')){
    suggestions = ['What is sesame export price?','How to harvest sesame?','Where to sell sesame in Nigeria?','How to store sesame after harvest?'];
  } else if(a.includes('cocoa')){
    suggestions = ['How to ferment cocoa beans?','What is cocoa price today?','How to control cocoa black pod?','How to improve cocoa yield?'];
  } else if(a.includes('cashew')){
    suggestions = ['When is cashew harvest season?','What is cashew export price?','How to process cashew nuts?','Where to sell cashew in Nigeria?'];
  }
  // Soil-related follow-ups
  else if(a.includes('soil') || a.includes('pH') || a.includes('acidic') || a.includes('fertile')){
    suggestions = ['How do I test my soil pH?','How much lime should I apply?','What fertilizer for sandy soil?','How to improve soil fertility?'];
  } else if(a.includes('fertilizer') || a.includes('npk') || a.includes('urea')){
    suggestions = ['When should I apply fertilizer?','What is the correct fertilizer dose?','How to prevent fertilizer burn?','Where to buy fertilizer cheaply?'];
  }
  // Market and investment follow-ups
  else if(a.includes('invest') || a.includes('roi') || a.includes('profit') || a.includes('return')){
    suggestions = ['What crops have highest ROI in Nigeria?','How do I access agricultural finance?','What are the best states for farming investment?','How do I export Nigerian farm products?'];
  } else if(a.includes('export') || a.includes('market') || a.includes('price') || a.includes('sell')){
    suggestions = ['What is the current market price?','How do I export from Nigeria?','When is the best time to sell?','Which market pays the best price?'];
  } else if(a.includes('storage') || a.includes('store') || a.includes('hermetic')){
    suggestions = ['How long can I store grain safely?','How to prevent weevils in stored grain?','What is the best storage method?','How to use hermetic bags?'];
  }
  // Weather follow-ups
  else if(a.includes('rain') || a.includes('drought') || a.includes('flood') || a.includes('season')){
    suggestions = ['When does planting season start?','How to manage drought stress?','What crops survive flooding?','When is the dry season?'];
  }
  // Disease/pest follow-ups
  else if(a.includes('disease') || a.includes('pest') || a.includes('wilt') || a.includes('blight') || a.includes('fungus')){
    suggestions = ['How do I treat this disease?','What fungicide should I use?','How to prevent crop disease?','What is the cost of treatment?'];
  }
  // Default follow-ups
  else {
    if(activeLang === 'ha'){
      suggestions = ['Wane taki zan yi amfani?','Yaushe lokacin girbi?','Nawa ake siyarwa a kasuwa?','Yaya zan hana cututtuka?'];
    } else {
      suggestions = ['What crops are most profitable?','How do I improve my soil?','What is the current market price?','How do I access farm credit?'];
    }
  }

  // Show 3 random suggestions from the list
  // Always add interactive options
  var interactive = activeLang === 'ha' ?
    ['Kara bayani', 'Cikakken bayani'] :
    ['Tell me more', 'Full detailed analysis'];
  var picks = suggestions.sort(function(){return 0.5-Math.random();}).slice(0,2).concat(interactive.slice(0,1));
  var bar = document.createElement('div');
  bar.id = 'followup-bar';
  bar.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;padding:6px 12px;';
  picks.forEach(function(q){
    var btn = document.createElement('button');
    btn.textContent = q;
    btn.style.cssText='background:rgba(255,255,255,0.658);border:1px solid rgba(20,60,20,0.15);color:#123a12;border-radius:20px;padding:4px 12px;font-size:.75em;font-weight:500;cursor:pointer;';
    btn.onclick = function(){ inp.value = q; doSend(); };
    bar.appendChild(btn);
  });
  var m = document.getElementById('msgs') || msgs;
  m.appendChild(bar);
  m.scrollTop = m.scrollHeight;
}

inp.addEventListener('input', function(){
  inp.style.height = 'auto';
  inp.style.height = Math.min(inp.scrollHeight, 110) + 'px';
});
inp.addEventListener('keydown', function(e){
  if(e.key === 'Enter' && !e.shiftKey){ e.preventDefault(); doSend(); }
});
sbtn.addEventListener('click', doSend);

function startChat(){
  if(!started){
    started = true;
    welcome.style.display = 'none';
    chat.style.display = 'flex';
    chat.style.flexDirection = 'column';
  }
  var cb = document.getElementById('close-chat-btn');
  if(cb) cb.style.display = 'block';
}

function closeChatToHome(){
  saveChat();
  msgs.innerHTML = '';
  ci = -1;
  started = false;
  welcome.style.display = 'flex';
  chat.style.display = 'none';
  var cb = document.getElementById('close-chat-btn');
  if(cb) cb.style.display = 'none';
}

function addMsg(type, text){
  var d = document.createElement('div');
  d.className = 'msg ' + type;
  var av = document.createElement('div');
  av.className = 'av';
  av.textContent = type === 'b' ? '🌿' : '👤';
  var b = document.createElement('div');
  b.className = 'bbl';
  b.style.wordBreak = 'break-word';
  b.style.whiteSpace = 'pre-wrap';
  function renderInline(container, str){
    // Strip markdown heading markers
    str = str.replace(/^#{1,6}\s*/, '');
    // Split on **bold** markers and build DOM nodes
    var parts = str.split(/(\*\*[^*]+\*\*)/g);
    parts.forEach(function(part){
      if(!part) return;
      var m = part.match(/^\*\*([^*]+)\*\*$/);
      if(m){
        var strong = document.createElement('strong');
        strong.textContent = m[1];
        container.appendChild(strong);
      } else {
        container.appendChild(document.createTextNode(part));
      }
    });
  }

  // Split into bullet items: break on newlines AND on inline bullet markers like '•' or '- '
  var rawLines = text.split(/\n+/);
  var lines = [];
  rawLines.forEach(function(rl){
    var pieces = rl.split(/(?=•)|(?=\s-\s)/).map(function(p){ return p.trim(); }).filter(Boolean);
    if(pieces.length > 1){
      lines = lines.concat(pieces);
    } else {
      lines.push(rl.trim());
    }
  });

  var hasBullets = lines.some(function(l){ return l.startsWith('-') || l.startsWith('•') || l.startsWith('*') || /^\d+\./.test(l); });

  if(hasBullets || lines.length > 1){
    lines.forEach(function(line){
      line = line.trim().replace(/^#{1,6}\s*/, '');
      if(!line) return;
      var isBullet = line.startsWith('-') || line.startsWith('•') || line.startsWith('*') || /^\d+\./.test(line);
      if(isBullet){
        var li = document.createElement('div');
        li.style.cssText = 'padding:2px 0 2px 14px;position:relative;';
        var dot = document.createElement('span');
        dot.style.cssText = 'position:absolute;left:2px;color:#4CAF50;font-weight:bold;';
        dot.textContent = '•';
        li.appendChild(dot);
        var clean = line.replace(/^[-•*]\s*/,'').replace(/^\d+\.\s*/,'');
        renderInline(li, clean);
        b.appendChild(li);
      } else {
        var p = document.createElement('p');
        p.style.margin = '0 0 4px 0';
        renderInline(p, line);
        b.appendChild(p);
      }
    });
  } else {
    renderInline(b, text.replace(/^#{1,6}\s*/, ''));
  }
  d.appendChild(av);
  d.appendChild(b);
  if(type === 'b'){
    var bar = document.createElement('div');
    bar.style.cssText = 'display:flex;gap:6px;margin-top:4px;padding-left:36px;';
    var cb = document.createElement('button');
    cb.innerHTML = '&#128203;';
    cb.title = 'Copy';
    cb.style.cssText = 'background:none;border:none;color:#90d090;font-size:16px;cursor:pointer;opacity:0.7;';
    cb.onclick = function(){
      navigator.clipboard.writeText(b.textContent).then(function(){
        cb.innerHTML = '&#10003;';
        setTimeout(function(){ cb.innerHTML = '&#128203;'; }, 1500);
      });
    };
    var rb = document.createElement('button');
    rb.innerHTML = '&#8635;';
    rb.title = 'Refresh';
    rb.style.cssText = 'background:none;border:none;color:#90d090;font-size:16px;cursor:pointer;opacity:0.7;';
    rb.onclick = function(){
      var allU = msgs.querySelectorAll('.msg.u .bbl');
      if(allU.length === 0) return;
      var last = allU[allU.length - 1].textContent;
      var allB = msgs.querySelectorAll('.msg.b');
      if(allB.length > 0) allB[allB.length - 1].remove();
      inp.value = last;
      doSend();
    };
    bar.appendChild(cb);
    bar.appendChild(rb);
    d.appendChild(bar);
  }
  if(type === 'u'){
    var bar2 = document.createElement('div');
    bar2.style.cssText = 'display:flex;gap:6px;margin-top:4px;justify-content:flex-end;padding-right:36px;';
    var eb = document.createElement('button');
    eb.innerHTML = '&#9998;';
    eb.title = 'Edit';
    eb.style.cssText = 'background:none;border:none;color:#90d090;font-size:16px;cursor:pointer;opacity:0.7;';
    eb.onclick = function(){
      inp.value = b.textContent;
      inp.focus();
      d.remove();
    };
    bar2.appendChild(eb);
    d.appendChild(bar2);
  }
  msgs.appendChild(d);
  msgs.scrollTop = msgs.scrollHeight;
}

function addTyping(){
  var d = document.createElement('div');
  d.className = 'msg b'; d.id = 'typing';
  var av = document.createElement('div');
  av.className = 'av'; av.textContent = '🌿';
  var b = document.createElement('div');
  b.className = 'bbl'; b.textContent = '...';
  d.appendChild(av); d.appendChild(b);
  msgs.appendChild(d);
  msgs.scrollTop = msgs.scrollHeight;
}

function removeTyping(){
  var t = document.getElementById('typing');
  if(t) t.remove();
}

function doSend(){
  var text = inp.value.trim();
  if(!text) return;
  startChat();
  inp.value = '';
  inp.style.height = 'auto';
  sbtn.disabled = true;
  lastQuestion = text;
  var sentChatId = ci;
  addMsg('u', text);
  addTyping();
  fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      question: (text === 'Tell me more' || text === 'Full detailed analysis' || text === 'Kara bayani')
        ? lastQuestion
        : text,
      elaborate: (text === 'Tell me more' || text === 'Full detailed analysis' || text === 'Kara bayani'),
      lang: activeLang
    })
  }).then(function(r){ return r.json(); })
    .then(function(data){
      if(sentChatId !== ci){
        // User switched chats while this was in flight; save answer into the correct chat silently
        var ans2 = data.answer || 'Sorry, something went wrong.';
        if(sentChatId >= 0 && sentChatId < chats.length){
          chats[sentChatId].html += '<div class="msg b"><div class="av">\ud83c\udf3f</div><div class="bbl">' + ans2.replace(/</g,'&lt;') + '</div></div>';
        }
        sbtn.disabled = false;
        return;
      }
      removeTyping();
      var ans = data.answer || 'Sorry, something went wrong.';
      lastAnswer = ans;
      addMsg('b', ans);
      showFollowups(ans);
      sbtn.disabled = false;
      setTimeout(saveChat, 200);
    })
    .catch(function(){
      removeTyping();
      addMsg('b', 'Sorry, something went wrong.');
      sbtn.disabled = false;
    });
}

function drop(){
  var d = document.createElement('div');
  d.className = 'drop';
  var s = Math.random() * 5 + 2;
  d.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + Math.random() * 100 + '%;animation-duration:' + (Math.random() * 3 + 2) + 's;';
  document.body.appendChild(d);
  setTimeout(function(){ d.remove(); }, 5000);
}
setInterval(drop, 900);
for(var i = 0; i < 8; i++) drop();

var chats = [], ci = -1, lastQuestion = '', lastAnswer = '';
function openSB(){ document.getElementById('sd').style.left = '0'; document.getElementById('sd-ov').style.display = 'block'; }
function closeSB(){ document.getElementById('sd').style.left = '-270px'; document.getElementById('sd-ov').style.display = 'none'; }
function saveChat(){
  var ms = msgs.querySelectorAll('.msg');
  if(ms.length === 0) return;
  var lbl = msgs.querySelector('.msg.u .bbl');
  var label = lbl ? lbl.textContent.slice(0, 35) + '...' : ('Chat ' + (chats.length + 1));
  var html = Array.from(ms).map(function(m){ return m.outerHTML; }).join('');
  if(ci >= 0 && ci < chats.length){ chats[ci] = {label: label, html: html}; }
  else{ chats.push({label: label, html: html}); ci = chats.length - 1; }
  renderHist();
}
function renderHist(){
  var q = (document.getElementById('sb-q') || {}).value || '';
  q = q.toLowerCase();
  var h = document.getElementById('hist');
  if(!h) return;
  h.innerHTML = '';
  chats.forEach(function(c, i){
    if(q && c.label.toLowerCase().indexOf(q) < 0) return;
    var row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;gap:4px;';
    var d = document.createElement('div');
    d.className = 'hi' + (i === ci ? ' active' : '');
    d.style.flex = '1';
    d.textContent = c.label;
    d.onclick = function(){ saveChat(); ci = i; msgs.innerHTML = chats[i].html; msgs.scrollTop = msgs.scrollHeight; renderHist(); closeSB(); startChat(); };
    var del = document.createElement('button');
    del.innerHTML = '&times;';
    del.title = 'Delete chat';
    del.style.cssText = 'background:none;border:none;color:#c0392b;font-size:16px;cursor:pointer;padding:2px 8px;';
    del.onclick = function(e){
      e.stopPropagation();
      chats.splice(i, 1);
      if(ci === i){
        msgs.innerHTML = '';
        ci = -1;
        started = false;
        welcome.style.display = 'block';
        chat.style.display = 'none';
        var cb = document.getElementById('close-chat-btn');
        if(cb) cb.style.display = 'none';
      } else if(ci > i){
        ci = ci - 1;
      }
      renderHist();
    };
    row.appendChild(d);
    row.appendChild(del);
    h.appendChild(row);
  });
}
function newChat(){
  saveChat(); msgs.innerHTML = ''; ci = -1;
  addMsg('b', 'Welcome to VerdeBuddy! Ask me about crops, soil, weather, or market prices.');
  closeSB();
}
function navChat(dir){
  var ni = ci + dir;
  if(ni >= 0 && ni < chats.length){ saveChat(); ci = ni; msgs.innerHTML = chats[ni].html; msgs.scrollTop = msgs.scrollHeight; renderHist(); }
}
document.addEventListener('DOMContentLoaded', function(){
  document.getElementById('sb-tog').onclick = openSB;
  document.getElementById('sb-cls').onclick = closeSB;
  document.getElementById('sd-ov').onclick = closeSB;
  document.getElementById('sb-new').onclick = newChat;
  document.getElementById('sb-q').oninput = renderHist;
  document.getElementById('sb-bk').onclick = function(){ navChat(-1); };
  document.getElementById('sb-fw').onclick = function(){ navChat(1); };
});