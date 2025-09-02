let mediaRecorder;
let chunks = [];

const recordBtn = document.getElementById("recordBtn");
const audioPlayer = document.getElementById("audioPlayer");
const messages = document.getElementById("messages");

recordBtn.onmousedown = startRecording;
recordBtn.onmouseup = stopRecording;
recordBtn.ontouchstart = startRecording;
recordBtn.ontouchend = stopRecording;

function startRecording() {
  navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = e => chunks.push(e.data);
    mediaRecorder.onstop = sendAudioToServer;

    mediaRecorder.start();
    recordBtn.innerText = "🔴 Recording...";
  });
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    recordBtn.innerText = "🎤 Hold to Talk";
  }
}

function appendMessage(text, sender) {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.innerText = text;
  messages.appendChild(msg);
  messages.scrollTop = messages.scrollHeight;
}

function sendAudioToServer() {
  const blob = new Blob(chunks, { type: "audio/webm" });
  const formData = new FormData();
  formData.append("audio", blob);

  appendMessage("🧠 Processing your voice...", "user");

  fetch("http://127.0.0.1:8000/process-audio", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      const { user_text, bot_reply, audio_base64 } = data;

      appendMessage(user_text, "user");
      appendMessage("🔈 AI is responding...", "bot");

      const audioBlob = base64ToBlob(audio_base64, "audio/wav");
      const url = URL.createObjectURL(audioBlob);
      audioPlayer.src = url;
      audioPlayer.play();

      audioPlayer.onended = () => {
        appendMessage(bot_reply, "bot");
      };
    });
}

function base64ToBlob(base64, mime) {
  const binary = atob(base64);
  const array = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    array[i] = binary.charCodeAt(i);
  }
  return new Blob([array], { type: mime });
}
