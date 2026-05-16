Local React Demo Testing (Mac / Local Node)

1. Go to project folder:
cd ~/balena-hello/react-demo

2. First-time install (or after deleting node_modules):
npm install

3. Run locally:
npm start

4. Open browser:
http://localhost:3000

----------------------------------------
Common Local Issue
----------------------------------------
If /data log path errors occur, either:
- Create local /data folder
OR
- Update server.js to use local fallback logging

----------------------------------------
Stop local server
----------------------------------------
CTRL + C

----------------------------------------
Clean local-only files
----------------------------------------
rm -rf node_modules react-demo.log

Optional:
rm -f package-lock.json

----------------------------------------
Check folder
----------------------------------------
ls -lah

Expected core files:
Dockerfile
package.json
server.js
services.json

----------------------------------------
Reinstall from clean
----------------------------------------
npm install
npm start

----------------------------------------
Git safety
----------------------------------------
Do NOT commit:
node_modules/
*.log

Check:
git status

----------------------------------------
Balena Deploy
----------------------------------------
From project root:
cd ~/balena-hello
balena push timothy_reinhardt/moonintheman
