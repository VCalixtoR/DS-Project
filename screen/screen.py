from configparser import ConfigParser
import os

config_obj = ConfigParser()
config_obj.read(os.path.abspath('config.ini'))

screenLineSize = int(config_obj['screen']['line_size'])
screenIndentN = int(config_obj['screen']['indent_n'])
screenWrapperLR = '█'
screenWrapperTop = '▀'
screenWrapperBOT = '▄'

def screenFormatTitle(strTitle):
  global screenLineSize, screenWrapperLR

  if len(strTitle) > screenLineSize-4:
    return screenFormatLine(strTitle)
  
  totalSpacesN = screenLineSize-len(strTitle)-2
  leftSpacesN = int(totalSpacesN/2)
  rightSpacesN = totalSpacesN-leftSpacesN

  return screenWrapperLR + (' ' * leftSpacesN) + strTitle + (' ' * rightSpacesN) + screenWrapperLR

def screenFormatLine(str=None, nIndents=1):
  global screenLineSize, screenWrapperLR, screenIndentN

  if not str:
    return screenWrapperLR + (' ' * (screenLineSize-2)) + screenWrapperLR

  resultStr = screenWrapperLR + (' ' * (screenIndentN * nIndents))
  linepos = 1 + (screenIndentN * nIndents)
  
  words = str.split()
  wIndex = 0

  while wIndex < len(words):
    word = words[wIndex]

    if linepos == 0:
      resultStr = resultStr + screenWrapperLR + (' ' * (screenIndentN * (nIndents+1)))
      linepos = 1 + (screenIndentN * (nIndents+1))

    # last word of the line, word does not break line
    if (linepos+len(word)+2) <= screenLineSize and (linepos+len(word)+2) > screenLineSize-6:
      resultStr = resultStr + word + (' ' * (screenLineSize-(linepos+len(word)+2)) ) + ' ' + screenWrapperLR
      linepos = 0

      # only add new line if word is not the last of str
      if(wIndex+1 < len(words)):
        resultStr = resultStr + '\n'
    
    # last word of the line, word break line
    elif (linepos+len(word)+2) > screenLineSize:
      worDivN = len(word) - ( (linepos+len(word)+2) - screenLineSize )
      resultStr = resultStr + word[0:worDivN] + ' ' + screenWrapperLR + '\n'

      # characters that exceed the current line size will be processed again as a normal word
      words[wIndex] = word[worDivN:len(word)]
      wIndex = wIndex - 1
      linepos = 0
    
    # not last word of the line but last word of str
    elif wIndex+1 == len(words):
      resultStr = resultStr + word + (' ' * (screenLineSize-len(word)-linepos-1)) + screenWrapperLR
    
    # not last word of the line
    else:
      resultStr = resultStr + word + ' '
      linepos = linepos+len(word)+1
    
    wIndex = wIndex + 1
  
  return resultStr

def screenFormatDict(data, nIndents=1):

  nestedDictStr = ''

  for key in data.keys():
    
    if not isinstance(data[key], dict):
      nestedDictStr = nestedDictStr + screenFormatLine(str(key) + ': ' + str(data[key]), nIndents) + '\n'
    else:
      nestedDictStr = nestedDictStr + screenFormatLine(str(key) + ':', nIndents) + '\n' + screenFormatDict(data[key], nIndents+1)
    
  return nestedDictStr

def screenMountReturnNextStep(title, description, options=None, inputLabels=None, dictData=None, arrayDictData=None, clear=True):
  global screenLineSize, screenWrapperLR, screenWrapperTop, screenWrapperBOT, screenIndentN
  
  screenStr = '\n'

  # title
  screenStr = screenStr + screenWrapperLR + (screenWrapperTop * (screenLineSize-2)) + screenWrapperLR + '\n'
  screenStr = screenStr + screenFormatTitle(title) + '\n'
  screenStr = screenStr + screenWrapperLR + (screenWrapperBOT * (screenLineSize-2)) + screenWrapperLR + '\n'

  # description
  screenStr = screenStr + screenFormatLine() + '\n'
  screenStr = screenStr + screenFormatLine(description) + '\n'
  screenStr = screenStr + screenFormatLine() + '\n'

  # dict description(could be nested)
  if dictData and type(dictData) == dict:
    screenStr = screenStr + screenFormatDict(dictData)
    screenStr = screenStr + screenFormatLine() + '\n'
  
  if arrayDictData and type(arrayDictData) == list:
    for aDictD in arrayDictData:
      screenStr = screenStr + screenFormatDict(aDictD)
      screenStr = screenStr + screenFormatLine() + '\n'

  # options
  if options:
    screenStr = screenStr + screenFormatLine('Options: ') + '\n'
    screenStr = screenStr + screenFormatLine() + '\n'

    for optIndex in range(len(options)):
      screenStr = screenStr + screenFormatLine(str(optIndex + 1) + ': ' + options[optIndex], 2) + '\n'
    
    screenStr = screenStr + screenFormatLine() + '\n'

  screenStr = screenStr + screenWrapperLR + (screenWrapperBOT * (screenLineSize-2)) + screenWrapperLR + '\n'

  if clear:
    os.system('cls||clear')
  
  print(screenStr)

  ret = None

  # select options
  if (not inputLabels) and options:
    ret = input( (' ' * screenIndentN) + 'Choose an option: ')
    
    while True:
      if(ret.isdigit()):
        if( int(ret) > 0 and int(ret) <= len(options) ):
          break
      ret = input((' ' * screenIndentN) + 'Invalid option: Choose another: ')
    
    ret = int(ret)
  
  # input data
  elif inputLabels:
    ret = dict()
    for inputLabel in inputLabels:
      ret[inputLabel] = input(inputLabel + ': ')
  
  # press enter to continue
  else:
    input('Press enter to continue')

  return ret

def screenCacheMount(title, cacheData, clear=False):
  global screenLineSize, screenWrapperLR, screenWrapperTop, screenWrapperBOT

  screenStr = '\n'

  # title
  screenStr = screenStr + screenWrapperLR + (screenWrapperTop * (screenLineSize-2)) + screenWrapperLR + '\n'
  screenStr = screenStr + screenFormatTitle(title) + '\n'
  screenStr = screenStr + screenWrapperLR + (screenWrapperBOT * (screenLineSize-2)) + screenWrapperLR + '\n'

  # dict description(could be nested)
  if type(cacheData) == dict:
    screenStr = screenStr + screenFormatDict(cacheData)
    screenStr = screenStr + screenFormatLine() + '\n'

  screenStr = screenStr + screenWrapperLR + (screenWrapperBOT * (screenLineSize-2)) + screenWrapperLR + '\n'

  if clear:
    os.system('cls||clear')
  print(screenStr)