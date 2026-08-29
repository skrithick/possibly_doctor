// There's probably some better way to do all this
// But I've done it to the extent of javascript I know

const chat_link = document.getElementById('chat-link')
const about_link = document.getElementById('about-link')
const chat_form = document.getElementById('chat-form')
const chat_input =  document.getElementById('chat-input')
const chat_button = document.getElementById('chat-submit')
const chat_window = document.getElementById('chat-window')
const about_window = document.getElementById('about-window')
const chat_messages = document.getElementById('chat-messages')
const new_button = document.getElementById('new')

let first = true
const default_message = '<i>The rag has memory of chat upto last 5 messages, so follow-ups can be asked. To start a new session click on the new button on the left.</i> <i>The response will have subcontent showing (in this order): Urgency Level, Confidence, Overconfidence, and Sources</i>'

about_window.classList.add('hidden')
chat_link.classList.add('focused')

window.addEventListener('load', () => {
    fetch('http://127.0.0.1:8000/api/forget', { method: "GET" })
        .then(() => console.log('New session'))
})

new_button.addEventListener('click', e => {
    fetch('http://127.0.0.1:8000/api/forget', {
        method: "GET",
    }).then(() => {
        chat_messages.innerHTML = default_message
        about_window.classList.add('hidden')
        chat_link.classList.add('focused')
        chat_button.innerHTML = `<i class="ti ti-send"></i>`
        console.log('New session')
    })
})

chat_link.addEventListener('click', e => {
    chat_window.classList.remove('hidden')
    chat_link.classList.add('focused')
    about_window.classList.add('hidden')
    about_link.classList.remove('focused')
    chat_button.disabled = false
})

about_link.addEventListener('click', e => {
    chat_window.classList.add('hidden')
    chat_link.classList.remove('focused')
    about_window.classList.remove('hidden')
    about_link.classList.add('focused')
})

function addUserMessage(content) {
    chat_messages.innerHTML += `
    <div class="message user" id="message from:user">
        ${content}
    </div>
    `
}

function addRAGMessage(content, confidence, citations, urgency_level, overconfidence) {
    let classification = ''
    switch (urgency_level) {
        case 2:
            classification = 'Medium'
            break
        case 3:
            classification = 'Severe'
            break
        default:
            classification = 'Low'
    }

    chat_messages.innerHTML += `
    <div class="message rag" id="message from:rag">
        ${content}
        <ul class="sub-message">
            <li class="b">${classification}</li>
            <li class="b">${confidence}</li>
            <li class="b">${overconfidence}</li>
            <li>Sources: ${citations.join(' / ')}</li>
        </ul>
    </div>
    `
}

chat_form.addEventListener('submit', e => {
    e.preventDefault()

    const user_input = chat_input.value
    addUserMessage(user_input)

    chat_button.disabled = true
    chat_button.classList.add('disabled')
    chat_button.innerHTML = `<i class="ti ti-refresh-dot icon-rotate"></i>`
    chat_input.value = ''

    fetch('http://127.0.0.1:8000/api/chat', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            question: user_input,
        })
    }).then(res => {
        if (!res.ok) {
            throw new Error(`HTTP Error - Status: ${res.status}`);
        }
        return res.json()
    }).then(({urgency_level, confidence, response, citations, overconfidence}) => {
        console.log(response, citations)
        addRAGMessage(response, confidence, citations, urgency_level, overconfidence)
        chat_button.disabled = false
        chat_button.classList.remove('disabled')
        chat_button.innerHTML = `<i class="ti ti-send"></i>`
    })
})