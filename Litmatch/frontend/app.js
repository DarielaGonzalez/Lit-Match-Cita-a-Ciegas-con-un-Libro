const API = 'http://127.0.0.1:8000/api'
let token = null

document.getElementById('register-form').addEventListener('submit', async (e)=>{
  e.preventDefault()
  const email = document.getElementById('reg-email').value
  const password = document.getElementById('reg-pass').value
  const res = await fetch(`${API}/register`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({email, password})
  })
  const j = await res.json()
  if (res.ok) {
    token = j.token
    showPanel(j.user)
  } else alert(j.detail || JSON.stringify(j))
})

document.getElementById('login-form').addEventListener('submit', async (e)=>{
  e.preventDefault()
  const email = document.getElementById('login-email').value
  const password = document.getElementById('login-pass').value
  const res = await fetch(`${API}/login`, {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({email, password})
  })
  const j = await res.json()
  if (res.ok) {
    token = j.token
    showPanel(j.user)
  } else alert(j.detail || JSON.stringify(j))
})

function showPanel(user){
  const panel = document.getElementById('panel')
  panel.innerHTML = `
    <p>Bienvenido, ${user.email}</p>
    <h3>Cuestionario (Ejemplo)</h3>
    <textarea id="q-answers" rows="4" cols="50" placeholder="Escribe tus respuestas..."></textarea><br/>
    <button id="send-q">Enviar cuestionario</button>
    <h3>Registrar Libro (como autor)</h3>
    <input id="book-title" placeholder="Título" /><br/>
    <textarea id="book-desc" placeholder="Descripción"></textarea><br/>
    <button id="reg-book">Registrar libro</button>
    <h3>Recomendaciones</h3>
    <div id="recs"></div>
  `

  document.getElementById('send-q').addEventListener('click', async ()=>{
    const answers = document.getElementById('q-answers').value.split('\n').filter(Boolean)
    const form = new FormData()
    form.append('token', token)
    // Using JSON endpoint via fetch POST with application/json
    const res = await fetch(`${API}/questionnaire`, {
      method: 'POST', body: JSON.stringify({answers}), headers: {'Content-Type':'application/json'}
    })
    const j = await res.json()
    if (res.ok) {
      // call recommendation
      const rec = await fetch(`${API}/recommend`, {
        method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({user_embedding: j.embedding})
      })
      const rj = await rec.json()
      if (rec.ok) renderRecs(rj.results)
      else alert(JSON.stringify(rj))
    } else alert(JSON.stringify(j))
  })

  document.getElementById('reg-book').addEventListener('click', async ()=>{
    const title = document.getElementById('book-title').value
    const desc = document.getElementById('book-desc').value
    const form = new FormData()
    form.append('title', title)
    form.append('description', desc)
    form.append('token', token)
    const res = await fetch(`${API}/author/book`, {method: 'POST', body: form})
    const j = await res.json()
    if (res.ok) alert('Libro registrado: ' + j.book.title)
    else alert(JSON.stringify(j))
  })
}

function renderRecs(list){
  const out = document.getElementById('recs')
  if (!list || list.length === 0) out.innerText = 'No recommendations yet.'
  else out.innerHTML = list.map(b => `<div><strong>${b.title}</strong><p>${b.description}</p></div>`).join('\n')
}
