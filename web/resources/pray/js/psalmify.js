function formatHeader(header) {
  header = header.slice(1, -2).replace(':', '. ') + '.';
  numeral = header.match(/\s([IVXLC]+)[\s|\.]/);
  if (numeral) {
    numeral = numeral[1];
    vals = {'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1};
    number = 0;
    for (var j = 0; j < numeral.length; j++) {
      if (j != numeral.length - 1 && vals[numeral[j]] < vals[numeral[j + 1]]) {
        number += vals[numeral[j + 1]] - vals[numeral[j]];
        j++;
      } else {
        number += vals[numeral[j]];
      }
    }
  }
  return `[${header.replace(numeral, number)}]\n`;
}

function formatPsalm(psalm) {
  ret = '';
  for (p of psalm.split(/(\[.+?\]\n)/).slice(1)) {
    console.log(p);
    if (p.startsWith('[')) {
      ret += formatHeader(p);
    } else {
      ret += p;
    }
  }
  return ret;
}
