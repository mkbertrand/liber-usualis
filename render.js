const readLine = require('readline');
const rl = readLine.createInterface({input: process.stdin});

rl.on('line', (line) => {
  let request;
  try {
    request = JSON.parse(line);
  } catch (e) {
    process.stderr.write('Uh oh\n');
    return;
  }
  process.stdout.write(JSON.stringify({'id': request.id}) + '\n');
});
