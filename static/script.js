// static/script.js
// Clock
function updateClock(){
  const now = new Date();
  document.getElementById('time').innerText = now.toLocaleTimeString();
  document.getElementById('date').innerText = now.toLocaleDateString();
}
setInterval(updateClock,1000);
updateClock();

// copy buttons
document.addEventListener('click', function(e){
  const btn = e.target.closest('.copy-btn');
  if(!btn) return;
  const card = btn.getAttribute('data-card') || btn.dataset.card;
  navigator.clipboard.writeText(card).then(()=>{
    btn.innerText = 'Kopyalandı';
    setTimeout(()=> btn.innerText = 'Kopyala', 900);
  }).catch(()=> alert('Kopyalama başarısız'));
});

// clear
document.getElementById('clearBtn')?.addEventListener('click', function(){
  const ta = document.querySelector('textarea[name="kartlar"]');
  if(ta) ta.value = '';
});
