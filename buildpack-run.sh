#find /app -name \*.pyc -delete
cd /app/modules/mc-client
npm install
npm run build
npm run export