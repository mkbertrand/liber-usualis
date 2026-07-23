function formatPsalm(psalm) {
  headers = psalm.match(/\[.+?\]\n/g);
  for (let oldHeader of headers) {
    newHeader = oldHeader.slice(1, -2).replace(':', '. ') + '.';
    numeral = newHeader.match(/\s([IVXLC]+)[\s|\.]/);
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
      newHeader = newHeader.replace(numeral, number);
    }
    psalm = psalm.replace(oldHeader, '[' + newHeader + ']\n');
  }
  console.log(psalm);
  return psalm;
}
