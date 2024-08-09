'''
NLPPA: Natural Language Processing Presentation Assistant
UPDATED IN 09/08/2024 by /goktuggokce
'''
import torch
from transformers import pipeline
import speech_recognition as sr
from os import system
from gtts import gTTS
from time import sleep

model_id = "unsloth/llama-3-8b-Instruct-bnb-4bit"
tr_en_model_id = "Helsinki-NLP/opus-mt-tc-big-tr-en"

llama3pipeline = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={
        "torch_dtype": torch.float16,
        "quantization_config": {"load_in_4bit": True},
        "low_cpu_mem_usage": True,
    },
)
tr_en_pipe = pipeline(
    "translation",
    model=tr_en_model_id,
    device="cuda"
)

_TestRawList = [ # Sunulan konu başlıkları en fazla 9 olacak şekilde eklenmelidir.
    "En ünlü müzeler hangileridir?",
    "Bir müzenin amacı nedir?",
    "Müzelerde hangi tür koleksiyonlar bulunur?",
    "Müze ziyaretçilerine sunulan hizmetler nelerdir?",
    "Müzelerin tarihsel gelişimi nasıl olmuştur?",
    "Müzeler eğitim alanında nasıl bir rol oynar?",
    "Dijital müzecilik nedir ve ne gibi avantajlar sunar?",
    "Bir müzeyi ziyaret ederken nelere dikkat edilmelidir?",
    "Müze koleksiyonlarının korunması nasıl sağlanır?"
]
_MentionedList = [] # Tekrar önerilmeyecek konu başlıkları listesi (0, 1, 2, ...)

def Main(): # Fonksiyonların çalışma sırası
    input()
    Running(Start(_TestRawList))

def Start(_RawList): # Projenin hazırlık fonksiyonu
    _RefinedList = [] # Numaralandırma ve bağlantılı önem değişkenini tutması için düzenlenmiş liste
    for element in _RawList:
        elementPriority = None
        while not elementPriority in (str(1), str(0)):
          elementPriority = input(f"'{element}' Konusu sunum için önemli mi? (evet için 1, hayır için 0)\n>>")
        tempTuple = (element, int(elementPriority))
        _RefinedList.append(tempTuple)
    return _RefinedList

def Find_Recommendation(_SubjectCounter, _RefinedList): # Sonraki önerilecek konuyu bulma fonksiyonu
    if _SubjectCounter - 2 < 0 and _SubjectCounter >= -1: # Bahsedilen konunun öncesi var mı? Sonrası var mı?
      return _SubjectCounter
    elif _SubjectCounter > len(_RefinedList) or _SubjectCounter == -9: # Eşlenmedi durumu
      for topic in _RefinedList: # Tüm konu başlıklarını gez
        if not (_RefinedList.index(topic) in _MentionedList): # Anlatılmayan konu başlığına rastlarsan çıktısını ver
          return _RefinedList.index(topic)
      return None
    elif not _SubjectCounter - 2 in _MentionedList: # Önceki konu başlığı anlatılmadı mı?
      _IsPriority = _RefinedList[_SubjectCounter-2][1]
      if _IsPriority: # Anlatılmayan konu başlığı önemli mi?
        return _SubjectCounter - 2 # Önemli durumunda önceki konu başlığını çıktı ver
    elif not (_SubjectCounter >= len(_RefinedList)) and (not _SubjectCounter in _MentionedList): # Sonraki konu başlığı var mı ve anlatıldı mı?
      return _SubjectCounter
    for topic in _RefinedList: # Uyuşmayan durumlarda tüm konu başlıklarını gez ve anlatılmayanı çıktı ver
      if not (_RefinedList.index(topic) in _MentionedList):
        return _RefinedList.index(topic)
    return None

def Running(_RefinedList):
    def RecordAudio(): # Ses kaydı al ve çıktıyı ingilizce ver
        _r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Ses kayıt ediliyor..")
            audio = _r.listen(source)
            try:
                _RawAudio = _r.recognize_google(audio, language='tr-TR') # Ses kaydının türkçe ayarı
                print("Kayıt alınan ses metni: " + _RawAudio)
                return tr_en_pipe(_RawAudio)[0]['translation_text'] # Modelden ingilizce çevirisi
            except sr.UnknownValueError:
                print("Google Ses Tanıma, ses tanımlayamadı.")
                return None
            except sr.RequestError as e:
                print(f"Google Ses Tanıma'dan cevap alınamadı; Hata Mesajı: {e}")
                return None
        return None

    def DetectSubject(_RefinedAudio): # Alınan ses kaydının konu başlığı ile eşlenmesi
        def ConnectModel(_Input):
          messages = [
              {"role": "system", "content": "You are a assistant who willing to provide matching topic's number relatively given text"}, # Sistemin aldığı ilk prompt
              {"role": "user", "content": _Input}, # Cevabı beklenen prompt
          ]
          prompt = llama3pipeline.tokenizer.apply_chat_template(
                  messages,
                  tokenize=False,
                  add_generation_prompt=True
          )

          terminators = [
              llama3pipeline.tokenizer.eos_token_id,
              llama3pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
          ]

          outputs = llama3pipeline( # Llama3 entegrasyonu
              prompt,
              max_new_tokens=256,
              eos_token_id=terminators,
              do_sample=True,
              temperature=0.6,
              top_p=0.9,
          )
          _Answer = outputs[0]["generated_text"][len(prompt):].replace('.', '').replace('is', '').replace(':', '').replace('  ', ' ') # Model çıktısının işlenmesi
          numbers = ['1', '2', '3', '4', '5', '6' ,'7' ,'8' ,'9']
          print("DEBUG _Answer: " + _Answer)
          if "None" in _Answer: # Modelin girdi ile konuları eşleyemediği durum
            return "Nothing matched."
          if len(_Answer) > 3:
            if str(_Answer[_Answer.find("number") + 7]) in numbers: # Konu başlığının numarasının alınması
              output = str(_Answer[_Answer.find("number") + 7])
              '''
                if str(_Answer[_Answer.find("number") + 8]) in numbers:
                  return output + str(_Answer[_Answer.find("number") + 8])
              '''
              return output
          return _Answer

        _Input = ""
        i = 1
        for x in _RefinedList:
          _Input += f"{i}) {tr_en_pipe(x[0])[0]['translation_text']}\n" # Her bir konu başığının ingilizceye çevrilmesi
          i += 1
        _Input += (
            f"The text is: '{_RefinedAudio}'\nDoes this sentence match any of the listed topics? "
            "Please be as selective as possible. "
            "If there is a match, output must not include anything except matching topic's number. "
            "If there is no match, output must be only None. "
            "For example: Matching topic number 2" # Modele verilecek olan prompt
        )
        print(_Input)
        _Answer = ConnectModel(_Input=_Input) # Modelin cevabı alınır
        return _Answer
    while len(_MentionedList) < len(_RefinedList): # Bahsedilmeyen konu kaldıysa döngüsü
      _RefinedAudio = RecordAudio() # Ses kaydı alınır
      if _RefinedAudio == None: # Ses metni başarılı bir şekilde aldığının kontrolü
              continue
      print("DEBUG Çevrilmiş kayıt metni: " + _RefinedAudio)
      temp = 0
      _MentionedSubject = DetectSubject(_RefinedAudio) # Ses metninin konu başlığıyla eşleştirilmesi
      if _MentionedSubject == None: # Konu başlığı başarılı bir şekilde çıktısı döndürüldüğünün kontrolü
            continue
      if _MentionedSubject != "Nothing matched." and len(_MentionedSubject) < 2: # Konu başlığının eşleştirildiği durum
        _MentionedList.append(int(_MentionedSubject)-1) # Bahsedilenler listesine anlatılan konunun eklenmesi
        print("DEBUG Bahsedilen Konu: " + _TestRawList[int(_MentionedSubject)-1])
        ttemp = Find_Recommendation(int(_MentionedSubject), _RefinedList)
        if ttemp != None:
            temp = int(ttemp)+1 # Öneriecek konu başlığının seçimi
        else:
            print("Sunum başarı ile tamamlanmıştır.")
            break
      else:
        temp = Find_Recommendation(-9, _RefinedList)+1
      if temp:
        recommendation = int(temp-1)
        recommendation_text = _RefinedList[recommendation][0]
        print("Öneri: " + recommendation_text)
        gTTS(text = recommendation_text, lang='tr', slow=False).save("recommendation.mp3")
        system("start recommendation.mp3")
        sleep(7)

Main()