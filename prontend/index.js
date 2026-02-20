

const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");

// ── Helpers ──────────────────────────────────────────

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(text, sender) {
  // sender: "user" | "bot"
  const row = document.createElement("div");
  row.classList.add("message", sender);

  if (sender === "bot") {
    const avatar = document.createElement("div");
    avatar.classList.add("message-avatar");
    avatar.textContent = "🤖";
    row.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.classList.add("message-bubble");
  bubble.textContent = text;
  row.appendChild(bubble);

  chatMessages.appendChild(row);
  scrollToBottom();
}

/** Show / hide a typing indicator */
function showTyping() {
  const row = document.createElement("div");
  row.classList.add("message", "bot", "typing-indicator");

  const avatar = document.createElement("div");
  avatar.classList.add("message-avatar");
  avatar.textContent = "🤖";
  row.appendChild(avatar);

  const bubble = document.createElement("div");
  bubble.classList.add("message-bubble");
  bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
  row.appendChild(bubble);

  chatMessages.appendChild(row);
  scrollToBottom();
}

function removeTyping() {
  const el = chatMessages.querySelector(".typing-indicator");
  if (el) el.remove();
}

// ── Send flow ────────────────────────────────────────

async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  // 1. Show user message immediately
  addMessage(text, "user");
  chatInput.value = "";
  chatInput.focus();

  // 2. Show typing indicator while waiting
  showTyping();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await res.json();
    removeTyping();

    // 3. Show bot reply
    addMessage(data.ollama_response || "Sorry, I didn't understand that.", "bot");
  } catch (err) {
    removeTyping();
    addMessage("⚠️ Could not reach the server.", "bot");
    console.error(err);
  }
}

// ── Event listeners ──────────────────────────────────

sendBtn.addEventListener("click", sendMessage);

chatInput.addEventListener("keydown", function (e) {
  if (e.key === "Enter") sendMessage();
});