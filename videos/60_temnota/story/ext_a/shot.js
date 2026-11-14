// node shot.js in.svg out.png
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{const br=await chromium.launch();const p=await(await br.newContext({viewport:{width:1080,height:1920}})).newPage();
await p.goto('file://'+path.join(__dirname,'base.html'));await p.evaluate(()=>document.fonts.ready);
await p.evaluate(s=>{document.getElementById('c').innerHTML=s},fs.readFileSync(process.argv[2],'utf8'));
await p.screenshot({path:process.argv[3]});await br.close();})();
