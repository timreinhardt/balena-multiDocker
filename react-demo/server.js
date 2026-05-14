const express = require("express");
const fs = require("fs");

const app = express();
const PORT = 3000;

const LOG_FILE = "/data/react-demo.log";
const SERVICES_FILE = "/usr/src/app/services.json";

const APP_VERSION = "v1.6-central-services";

function log(message) {
  const line = `[${new Date().toISOString()}] ${message}`;
  console.log(line);

  try {
    fs.appendFileSync(LOG_FILE, line + "\n");
  } catch (err) {
    console.log("LOG FILE WRITE FAILED:", err.message);
  }
}

function loadServices() {
  try {
    return JSON.parse(fs.readFileSync(SERVICES_FILE, "utf8"));
  } catch (err) {
    log(`Failed to load services.json: ${err.message}`);
    return [];
  }
}

app.get("/", (req, res) => {
  const ip = req.hostname;
  const services = loadServices();

  const servicesHtml = services.map(service => `
    <li>
      <a href="http://${ip}:${service.port}${service.path}">
        ${service.name}
      </a>
    </li>
  `).join("");

  log("React service hub homepage requested");

  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>React Service Hub ${APP_VERSION}</title>

  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <style>
    body { background: #111; color: #00ff66; font-family: Arial; padding: 30px; }
    h1 { color: #00ccff; }
    .box { border: 1px solid #00ff66; padding: 20px; margin-bottom: 20px; }
    button { font-size: 20px; padding: 10px 18px; margin-top: 10px; }
    a { color: #00ccff; text-decoration: none; font-size: 18px; }
    li { margin: 12px 0; }
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
        <div>
          <h1>Balena Raspberry Pi Service Hub</h1>

          <div className="box">
            <p>Release: <b>${APP_VERSION}</b></p>
            <p>Balena service: <b>react-demo</b></p>
            <p>Pi IP: <b>${ip}</b></p>
            <p>Live browser time: <b>{time}</b></p>
            <p>Button count: <b>{count}</b></p>

            <button onClick={() => setCount(count + 1)}>
              Click me
            </button>
          </div>

          <div className="box">
            <h2>Available Services</h2>
            <ul>${servicesHtml}</ul>
            <p>Service list: <b>${SERVICES_FILE}</b></p>
            <p>Shared log file: <b>${LOG_FILE}</b></p>
          </div>
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
  log(`Starting React Service Hub | ${APP_VERSION}`);
  log("Open browser at: http://<PI-IP>:3000");
  log(`Service list file: ${SERVICES_FILE}`);
  log(`Shared log file: ${LOG_FILE}`);
  log("========================================");
});