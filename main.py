'''
NLPPA: Natural Language Processing Presentation Assistant
UPDATED IN 02/05/2024 by /goktuggokce
'''
import speech_recognition as sr

_TestRawList = ["AI (Artificial Intelligent) nedir?",
                "Yapay zeka tarihçesinin anlatımı",
                "Alanları nelerdir?",
                "Alt Alanları nelerdir?",
                "Geleceği nasıl etkileyecektir?"
                ]
_MentionedList = []

def Main():
    Running(Start(_TestRawList))

def Start(_RawList):
    _RefinedList = []
    for element in _RawList:
        elementPriority = None
        while not elementPriority in (str(1), str(0)):
            elementPriority = input(f"Is {element} has priority? (1 for yes, 0 for no)\n>>")
        tempTuple = (element, int(elementPriority))
        _RefinedList.append(tempTuple)
    return _RefinedList

def Find_Recommendation(_SubjectCounter, _RefinedList):
    if _SubjectCounter - 1 < 1 or _SubjectCounter + 1 > len(_RefinedList):
        return None
    if not _SubjectCounter - 1 in _MentionedList:
        _IsPriority = 0
        for element in _RefinedList:
            if _RefinedList.index(element) == _SubjectCounter - 1:
                for element_x, element_y in element:
                    _IsPriority = element_y
                    break
            break
        if _IsPriority:
            return _SubjectCounter - 1
        pass
    if not _SubjectCounter + 1 in _MentionedList:
        return _SubjectCounter + 1
    return None

def Running(_RefinedList):
    def RecordAudio():
        _r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Recording Audio..")
            audio = _r.listen(source)
            try:
                _RawAudio = _r.recognize_google(audio, language='tr-TR')
                print("Recorded Sentence: " + _RawAudio)
                return _RawAudio
            except sr.UnknownValueError:
                print("Google Speech Recognition couldn't recognize any word from record.")
                return None
            except sr.RequestError as e:
                print(f"Google Speech Recognition didn't respond; {e}")
                return None
        return None

    def FindIndexofMentionedSubject(_MentionedSubject):
        _MentionedSubjectIndex = None
        return _MentionedSubjectIndex

    def DetectSubject(_RefinedAudio):
        def ConnectGPT(_Input):
            _Answer = None
            return _Answer
        _Answer = ConnectGPT(_Input=_RefinedAudio)
        if _Answer in [_TestRawList]:
            return _Answer
        return None

    i = 1
    for x in _RefinedList:
        print(i, " ", x, "\n")
        i += 1

    _SubjectCounter = 0
    while (_SubjectCounter <= len(_RefinedList)):
        _RefinedAudio = RecordAudio()
        if _RefinedAudio == None:
            continue
        _MentionedSubject = DetectSubject(_RefinedAudio)
        if _MentionedSubject == None:
            continue
        _MentionedSubjectIndex = FindIndexofMentionedSubject(_MentionedSubject)
        if _MentionedSubjectIndex == None:
            continue
        _MentionedList.append(_MentionedSubjectIndex)
        _SubjectCounter = _MentionedSubjectIndex
        _Recommendation = Find_Recommendation(_SubjectCounter, _RefinedList)

Main()