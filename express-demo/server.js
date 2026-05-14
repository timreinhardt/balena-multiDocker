const express = require("express");

const app = express();
const PORT = 3000;

app.use(express.json());

let ledOn = false;
let counter = 0;

app.get("/", (req, res) => {
  res.send(`
    <html>
      <body style="font-family: Arial; padding: 30px;">
        <h1>Balena Express Demo</h1>

        <p>LED state: <b>${ledOn ? "ON" : "OFF"}</b></p>
        <p>Counter: <b>${counter}</b></p>

        <form action="/toggle" method="POST">
          <button>Toggle LED</button>
        </form>

        <form action="/count" method="POST">
          <button>Increment Counter</button>
        </form>

        <p><a href="/status">View JSON status</a></p>
      </body>
    </html>
  `);
});

app.get("/status", (req, res) => {
  res.json({ ledOn, counter });
});

app.post("/toggle", (req, res) => {
  ledOn = !ledOn;
  res.redirect("/");
});

app.post("/count", (req, res) => {
  counter += 1;
  res.redirect("/");
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Express demo running at http://<PI-IP>:${PORT}`);
});