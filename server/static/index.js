    async function sendCommand(red, green) {
      const resp = await fetch("/control-led", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ledRed: red, ledGreen: green})
      });
      const data = await resp.json();
      document.getElementById("status").innerText = data.message || data.error;
    }

    function toggle(id) {
      const btn = document.getElementById(id);
      const newState = btn.dataset.state === "0" ? 1 : 0;
      btn.dataset.state = newState;
      btn.innerText = `${id} = ${newState}`;
      // Only send the one LED change; others remain unchanged
      const other = id === "Red" ? Number(document.getElementById("Green").dataset.state) : Number(document.getElementById("Red").dataset.state);
      sendCommand(
        id === "Red"   ? newState : other,
        id === "Green" ? newState : other
      );
    }

