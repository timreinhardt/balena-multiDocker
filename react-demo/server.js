const express = require("express");
const fs = require("fs");

const app = express();
const PORT = 3000;
const LOG_FILE = "/data/react-demo.log";
const APP_VERSION = "v1.1-logging";

function log(message) {
  const line = `[${new Date().toISOString()}] ${message}`;
  console.log(line);

  try {
    fs.appendFileSync(LOG_FILE, line + "\n");
  } catch (err) {
    console.log("LOG FILE WRITE FAILED:", err.message);
  }
}

app.get("/", (req, res) => {
  log("React demo homepage requested");

  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>React Demo ${APP_VERSION}</title>
  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <style>
    body { background: #111; color: #00ff66; font-family: Arial; padding: 30px; }
    h1 { color: #00ccff; }
    .box { border: 1px solid #00ff66; padding: 20px; }
    button { font-size: 20px; padding: 10px 18px; margin-top: 10px; }
    a { color: #00ccff; }
  </style>
</head>

<body>
  <div id="root"></div>

  <script type="text/babel">
    function App() {
      const [count, setCount] = React.useState(0);
      const [time, setTime] = React.useState(new Date().toLocaleTimeString());

      React.useEffect(() => {
        const timer = setInterval(() => {
          setTime(new Date().toLocaleTimeString());
        }, 1000);

        return () => clearInterval(timer);
      }, []);

      return (
        <div className="box">
          <h1>React Demo on Raspberry Pi</h1>
          <p>Release: <b>${APP_VERSION}</b></p>
          <p>Balena service: <b>react-demo</b></p>
          <p>Live browser time: <b>{time}</b></p>
          <p>Button count: <b>{count}</b></p>

          <button onClick={() => setCount(count + 1)}>
            Click me
          </button>

          <hr />

          <p>
            Python Flask webcam app:
            <br />
            <a href="http://${req.hostname}:5000">
              http://${req.hostname}:5000
            </a>
          </p>

          <p>Local log file: <b>${LOG_FILE}</b></p>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById("root")).render(<App />);
  </script>
</body>
</html>
  `);
});

app.listen(PORT, "0.0.0.0", () => {
  log("========================================");
  log(`Starting React Demo | ${APP_VERSION}`);
  log(`Open browser at: http://<PI-IP>:${PORT}`);
  log(`Writing local logs to: ${LOG_FILE}`);
  log("========================================");
});