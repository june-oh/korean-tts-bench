import urllib.request as u, json, pathlib, subprocess, concurrent.futures
def fetch(model, files, folder):
 rev = {'s3':'aafc6e32416a594460b32413efc49d7fe4ce6d46','mms':'1b6491366d2ed6ea8e4e735607155d9f0110df29'}[folder]; d=json.load(u.urlopen('https://huggingface.co/api/models/'+model+'/revision/'+rev)); p=pathlib.Path(folder); p.mkdir(exist_ok=True); (p/'revision').write_text(d['sha'])
 def one(f):
  out=p/f;out.parent.mkdir(exist_ok=True);subprocess.run(['curl','--retry','3','-fsSL','https://huggingface.co/'+model+'/resolve/'+d['sha']+'/'+f,'-o',str(out)],check=True)
 with concurrent.futures.ThreadPoolExecutor(6) as e:list(e.map(one,[a['rfilename'] for a in d['siblings'] if files(a['rfilename'])]))
fetch('supertone-oss-archive/supertonic-3',lambda f:f.startswith('onnx/') or f=='voice_styles/F1.json','s3')
fetch('facebook/mms-tts-kor',lambda f:f in ['config.json','tokenizer_config.json','vocab.json','model.safetensors','special_tokens_map.json'],'mms')
