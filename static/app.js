
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
function setLang(lang){
  activeLang = lang;
  document.querySelectorAll('.lang-btn').forEach(function(b){
    b.style.background = b.dataset.lang === lang ? 'rgba(76,175,80,0.4)' : 'rgba(12,50,8,0.7)';
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
  var langMap = {en:'en-NG', ha:'ha-NG', yo:'yo', ig:'ig'};
  r.lang = langMap[activeLang] || 'en-NG';
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
var followups = {
  en: ['What fertilizer should I use?','When is the best time to sell?','How do I treat this disease?'],
  ha: ['Wane taki zan yi amfani?','Yaushe lokacin siyarwa?','Yaya zan magance wannan cuta?'],
  yo: ['Ajile wo ni mo lo?','Nigba wo ni akoko tita?','Bawo ni mo se wo arun yi?'],
  ig: ['Nri ala ole m ga-eji?','Kedu mgbe oge ire?','Kedu otu m ga-esi gwoo oria a?']
};
function showFollowups(){
  var existing = document.getElementById('followup-bar');
  if(existing) existing.remove();
  var fq = followups[activeLang] || followups.en;
  var bar = document.createElement('div');
  bar.id = 'followup-bar';
  bar.style.cssText = 'display:flex;gap:8px;flex-wrap:wrap;padding:6px 12px;';
  fq.forEach(function(q){
    var btn = document.createElement('button');
    btn.textContent = q;
    btn.style.cssText = 'background:rgba(12,50,8,0.8);border:1px solid #1a5c2a;color:#90d090;border-radius:20px;padding:4px 12px;font-size:.75em;cursor:pointer;';
    btn.onclick = function(){ inp.value = q; doSend(); };
    bar.appendChild(btn);
  });
  msgs.appendChild(bar);
  msgs.scrollTop = msgs.scrollHeight;
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
  b.textContent = text;
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
  addMsg('u', text);
  addTyping();
  fetch('/ask', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({question: text, lang: activeLang})
  }).then(function(r){ return r.json(); })
    .then(function(data){
      removeTyping();
      addMsg('b', data.answer || 'Sorry, something went wrong.');
      showFollowups();
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

var chats = [], ci = -1;
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
    var d = document.createElement('div');
    d.className = 'hi' + (i === ci ? ' active' : '');
    d.textContent = c.label;
    d.onclick = function(){ saveChat(); ci = i; msgs.innerHTML = chats[i].html; msgs.scrollTop = msgs.scrollHeight; renderHist(); closeSB(); };
    h.appendChild(d);
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