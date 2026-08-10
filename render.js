import readLine from 'readline'
import { renderRites } from './frontend/rite-renderer/rite-renderer.js';
import 'core-js/actual/set/index.js';
import fs from 'fs';

const resources = {
  'invitatoria': JSON.parse(fs.readFileSync('./data/generated/liber-usualis-chant/nocturnale/untagged/invitatoria.json')),
  'psalmTones': JSON.parse(fs.readFileSync('./data/generated/liber-usualis-chant/untagged/toni-psalmorum.json')),
};

const rl = readLine.createInterface({input: process.stdin});

rl.on('line', (line) => {
  let request;
  try {
    request = JSON.parse(line);
  } catch (e) {
    process.stderr.write(e.toString() + '\n');
    return;
  }
  try {
    process.stdout.write(JSON.stringify({'id': request.id, 'ret': renderRites(request.content, resources)}) + '\n');
  } catch (e) {
    process.stderr.write(e.stack + '\n');
    return;
  }
});
