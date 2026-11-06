# 한국어 TTS 청취실

[한국어 페이지](https://june-oh.github.io/korean-tts-bench/) · [English page](https://june-oh.github.io/korean-tts-bench/en.html)

관심 모델을 같은 한국어 난문장으로 직접 듣고 생성 시간까지 함께 확인할 비교 자료가 필요해 이 프로젝트를 시작했다. 직접 작성한 원고, 합성 결과와 측정 조건을 함께 공개한다.

16개 창작 문장으로 수사·날짜·금액·분수·받침·자모·영문·반복·억양을 비교한다. 무료 비상업 연구 데모이며 모든 음원은 AI 합성이다. 공개 원고는 총 541자(공백·문장부호 포함, 유니코드 코드포인트 기준). 개인 블라인드 모드는 현재 문장의 모델 순서를 무작위로 바꾸고 이름과 수치를 숨긴다. 청취자 투표, MOS, 인구집단 선호도 통계는 수집하지 않는다.

## 문장 선정

[KO-TTS Arena의 공개 문장](https://huggingface.co/spaces/channelcorp/KO-TTS-Arena/blob/30278887183752f87eae32811a807651845f886c/ko_prompts.json)에서 상품 코드·가격, 주문번호, 전화, 영문 혼용 안내 유형을 확인했다. [CoreaSpeech 논문](https://openreview.net/forum?id=8nHq0IIwpd)과 [저자 샘플](https://coreaspeech.github.io/demo/)에서 숫자·영문 정규화 및 numeric 시험셋을 검토했다. 기존 12문장을 이 기준으로 분류하고 번호·수량 대조, 편명, 긴 시각 변경 안내, 한글 정규화 대조군을 새로 작성했다. 원본 데이터셋 문장을 복제하거나 이 데모에서 원 논문의 성능을 재현했다고 주장하지 않는다.

## 측정 방법

2026-11-05, Apple M1 CPU. 모델을 메모리에 올리고 별도 문장으로 한 번 예열했다. 원문을 수정하거나 숫자를 읽는 방법을 미리 써 주지 않았다. 로컬 모델이 제공하는 전처리부터 전체 파형을 얻을 때까지 단조 시계로 3회 독립 측정했다. 동시 요청 1, 두 로컬 모델을 순차 실행했다. 로컬 모델 로딩·WAV 저장·브라우저 다운로드 시간은 제외했다. 사이트에는 각 문장의 **첫 번째 시도 음원 및 해당 시도 시간**을 표시한다. RTF는 그 시간 ÷ 해당 WAV 길이다. 서로 다른 기본 화자와 모델별 전처리도 결과에 영향을 준다. 원본 WAV는 음량 후처리나 실패 샘플 재선정 없이 보존한다. 기본 플레이어의 청취용 MP3는 파일별 고정 게인으로 −18 LUFS를 목표로 맞추되 인코딩 전 피크가 −2 dBTP를 넘지 않도록 제한한다. 듣기용 변환 시간은 생성 시간에서 제외했다. 적용 게인은 listen/모델ID/levels.json에 기록된다.

| 공개 모델·화자 | 실행 조건 | 원시 측정 · 체크포인트 리비전 |
|---|---|---|
| Supertone Supertonic 3 · F1 | ONNX CPU, 8 steps, speed 1.0 | [JSON](audio/supertonic3/measurements.json) |
| Meta MMS-TTS Korean · 단일 화자 | Transformers VITS, uroman, PyTorch CPU 4 threads | [JSON](audio/mms/measurements.json) |
| ElevenLabs Multilingual v2 · Hoon | 한국어 표준 화자 · 웹 합성 · 언어 한국어 · 시간 미측정 | [JSON](audio/eleven-hoon/measurements.json) |

ElevenLabs 음성은 **elevenlabs.io**에서 Free 플랜으로 직접 생성한 비상업 연구 샘플이다. 16문장 모두 Hoon - Calm Korean Narrator (voice ID 86GErZIiGJsPO3g7QNxZ)로 생성했다. 별도 결제 없이 한국어 언어 설정을 사용했다. 예전 영어 화자 Sarah의 속도는 Hoon의 그래프에서 제외했다.

[원문과 청취 포인트](prompts.json) · [모델 사양](models.json) · [합성 스크립트](scripts/generate.py)

## 문장별 성능 그래프

[그래프 보기](https://june-oh.github.io/korean-tts-bench/#timing) · [측정 CSV](figures/timings.csv). 저장소 루트에서 matplotlib와 numpy가 설치된 Python으로 `python scripts/plot_timings.py`를 실행한다. 한 점은 게시한 첫 시도의 측정값이고 마름모는 성공 문장의 단순 산술평균이다. 범위는 전체 최솟값~최댓값이다. RTF는 각 문장의 생성 시간을 그 문장의 원본 WAV 길이로 나눈 뒤 평균한다. CPU·GPU 장비가 섞여 있으며, 초회 모델 로드와 MP3 변환은 제외했다.

## 추가한 상업 이용 후보

| 후보 | 실제 시험 | 이용 조건과 선택 근거 |
|---|---|---|
| OpenBMB VoxCPM2 | 기본 생성 음성, BF16 스트리밍, CFG 2.0, 10 steps, 참조 음성·텍스트 정규화·재시도·torch.compile 비활성화. 예열 후 문장당 1회. | 코드·공식 가중치 Apache 2.0. 모델 카드가 한국어 및 상업 이용을 명시한다. 조회 당시 HF 최근 월간 다운로드 962,916회, GitHub 프로젝트 별 41,060개. [모델 카드](https://huggingface.co/openbmb/VoxCPM2) · [코드](https://github.com/OpenBMB/VoxCPM) |
| MyShell MeloTTS Korean | 기본 화자 KR, GPU FP32, speed 1.0. 예열 후 1회. P07 자모 ㄹ에서 KeyError로 실패해 그래프에는 성공한 15문장만 포함했다. | 코드·체크포인트 MIT. 한국어 전처리의 kykim/bert-kor-base는 배포 프로젝트에 Apache 2.0과 별도 상업 MOU 안내가 함께 있어 확인 필요. HF 한국어 체크포인트 최근 월간 다운로드 84,815회, GitHub 프로젝트 별 7,695개. [모델 카드](https://huggingface.co/myshell-ai/MeloTTS-Korean) · [코드](https://github.com/myshell-ai/MeloTTS) · [BERT 배포자](https://github.com/kiyoungkim1/LMkor) |

사용 지표는 2026-11-05 조회 당시 스냅샷이며 다운로드에 중복이 포함될 수 있다. 회사 제품에는 VoxCPM2와 기존 Qwen3-TTS(공식 체크포인트 Apache 2.0)를 먼저 검토할 수 있다. OmniVoice는 [가중치 라이선스](https://huggingface.co/k2-fsa/OmniVoice#license)가 CC-BY-NC여서 상업 후보에서 제외했다.

두 추가 모델은 RTX PRO 6000 Blackwell Server Edition GPU 각각 1장에서 측정했다. VoxCPM2의 첫 오디오 시간은 호출부터 CPU로 반환된 첫 비어 있지 않은 PCM 청크까지이며 사용자 기기의 재생 버퍼는 제외한다. 전체 스트림을 이어 붙여 게시한 파일과 같은 실행에서 측정했다. [합성 코드](scripts/generate_voxcpm2.py) · [첫 오디오 원시 기록](audio/voxcpm2/first_audio.json). voxcpm==2.0.3, PyTorch 2.9.1+cu128.

MeloTTS는 공식 코드 커밋 `209145371cff8fc3bd60d7be902ea69cbdb7965a`에 [한국어 모듈만 로드하는 패치](scripts/melotts-kr-imports.patch)를 적용했다. 공식 KR 전처리·BERT·기본 추론 설정을 사용했다. [실행 코드](scripts/generate_melo.py).

## 비용과 공개 조건

2026-11-05 기준. 일반 음성 파일 이용권, API 성능 비교 허가, 목소리 권리는 각각 확인한다. 공식 데모 녹음·타인의 복제 음성은 사용하지 않았다. 가중치는 이 저장소에 배포하지 않는다.

| 대상 | 이 규모의 비용 | 공개 처리 |
|---|---|---|
| GitHub Pages | 공개 저장소·정적 호스팅 $0. 사이트 최대 1GB, 월 전송량 소프트 한도 100GB | 재생할 때 TTS를 다시 호출하지 않는다. [GitHub 제한](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) |
| Supertonic 3 | 기존 CPU 사용, 외부 추론 요금 $0. 전기·장비비 별도 | OpenRAIL-M의 용도 제한과 합성물 표시 조건 적용. 제공자는 산출물에 권리를 주장하지 않으며 이용자가 책임진다. [라이선스](https://huggingface.co/supertone-oss-archive/supertonic-3/blob/main/LICENSE) |
| Meta MMS Korean | 기존 CPU 사용, 외부 추론 요금 $0 | Meta의 CC BY-NC 4.0 체크포인트로 비상업 연구용 생성. 가중치 라이선스를 모든 산출물에 포괄 재허락하지 않는다. [모델 카드](https://huggingface.co/facebook/mms-tts-kor) |
| ElevenLabs | 541자 × 3회 = 1,623자. $0.08/1천 자 모델은 약 $0.130, $0.04 모델은 약 $0.065의 사용량 상당액. 최소 결제·구독·세금 별도 | 직접 만든 음성은 플랜·보이스별 조건 확인. 무료는 비상업·출처 표시, 상업적 사용은 유료 조건. 다운로드 산출물의 외부 사용과 비교 벤치마크 허용 여부는 분리 검토. 계정별 계약 우선. [요금](https://elevenlabs.io/pricing/api) · [약관](https://elevenlabs.io/terms-of-use) · [개별 약관](https://elevenlabs.io/service-specific-terms) |
| Typecast SSFM | 같은 3회 시험 1,623크레딧. Lite 월 $15/20만 크레딧을 전량 소진한다고 보면 약 $0.122 상당. **허가 전 실행 보류** | API 약관에서 벤치마킹·경쟁 목적 성능/기능 모니터링을 제한. 유료 구독만으로 해결되지 않으므로 이 프로젝트의 음원 및 측정 결과 공개까지 서면 허가 후 추가. [API 약관 제3조 제한 사항](https://help.typecast.ai/en/articles/11872662-typecast-api-terms-of-use) · [요금](https://typecast.ai/pricing/api/) |
| Google Cloud TTS | 모델별 문자·토큰 단가, 무료 사용량·리전 확인 후 계산 | 서비스 약관 General Service Terms §7에서 고객 직접 시험, 재현 정보 제공, Google의 상응 시험·공개 허용 조건을 규정한다. 적용 계약·조항 확인 후 추가. [약관](https://cloud.google.com/terms/service-terms) · [요금](https://cloud.google.com/text-to-speech/pricing) |

## Qwen3-TTS 온프레미스 실행

공식 [Qwen3-TTS-12Hz-1.7B-CustomVoice](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)를 NVIDIA RTX PRO 6000 Blackwell Server Edition 1장으로 직접 실행했다. BF16, SDPA, 언어 Korean, 기본 화자 Sohee, qwen-tts 0.1.1을 사용했다. 별도 1문장으로 예열하고 동일한 16문장을 각각 1회 생성했다. 타이머는 CUDA 동기화를 포함하고 파일 저장은 제외한다. API 호출료는 없으며 GPU 전력·설비 비용은 별도다. 다른 로컬 모델의 M1 CPU 결과와 장비가 다르다. [재현 스크립트](scripts/generate_qwen.py) · [원시 시간과 가중치 리비전](audio/qwen3-tts-1p7b/measurements.json)

## 음원 추가하기

1. [prompts.json](prompts.json)의 원문을 그대로 넣어 합성한다. 저장소 밖 별도 디렉터리에 P01.wav … P16.wav로 보관한다. 부분 제출도 가능하다. 직접 녹음·생성했는지와 공개 권한을 확인한다.
2. 같은 디렉터리에 아래 예시의 model.json을 만들고 실제 값으로 바꾼다. access는 공개 가중치인 경우 open, 독점 서비스인 경우 closed로 설정한다. times.json은 선택 사항이다. 측정 기록이 없으면 생략한다. 파일의 재생 길이로 생성 시간을 추정하지 않는다.
3. 저장소 루트에서 아래 명령을 실행하고, 변경된 JSON과 추가 음원만 검토해 main에 커밋·푸시한다. GitHub Pages가 갱신된다.

```json
{"id":"my-run","access":"open","name":"모델명","voice":"프리셋·설정","device":"기기 또는 API 리전·시간 측정 범위","url":"https://example.org/model","license":"약관명","revision":"모델 버전·날짜","publication_basis":"직접 생성, 플랜, 출처 및 공개 근거 링크"}
```

```sh
python3 scripts/import_model.py /path/to/private-staging
```

times.json 예시 형식은 `{"P01":[1.25,1.31,1.21]}`. 첫 값은 반드시 게시 음원의 실측 시간(초)이다. API 결과는 서버 대기·네트워크를 포함할 수 있으므로 device에 측정 경계를 표시한다.

### ElevenLabs

기존 계정의 키를 로컬 환경변수 ELEVENLABS_API_KEY로 설정하고 게시 가능한 음성의 voice ID를 사용한다. **키는 Pages, 저장소, 브라우저 JavaScript에 넣지 않는다.** 아래 명령은 문장별 1회만 합성하며 실제 사용량이 발생한다. 중간에 멈췄다면 같은 경로로 다시 실행하면 성공 파일은 건너뛴다.

```sh
python3 scripts/elevenlabs.py VOICE_ID /path/to/private-staging
# macOS에서 MP3를 WAV로 변환. 네트워크 포함 실측은 times.json에 보존한다.
for f in /path/to/private-staging/*.mp3; do afconvert -f WAVE -d LEI16 "$f" "${f%.mp3}.wav"; done
```

플랜과 보이스 이용 조건 확인 후 model.json을 작성하고 위 가져오기 명령을 실행한다. 페이지 소스의 API 키나 방문자의 자격증명을 요구하지 않는다.

## 공개 모델 재현

Python 3.11 환경에서 아래 패키지를 설치한다. 별도 자산 디렉터리에서 fetch_assets.py를 실행하면 측정에 사용한 두 모델 리비전을 다운로드한다. 해당 디렉터리에 [Supertonic 공식 helper.py](https://raw.githubusercontent.com/supertone-oss-archive/supertonic/1e9799e964ea4c0dad7cde993b65c3c813a7b373/py/helper.py)를 helper.py로 저장한다. 저장소 루트에서 아래 순서로 실행한다. 기존 결과를 덮어쓰므로 재현용 복제본에서 실행한다.

```sh
pip install numpy==2.4.6 soundfile==0.14.0 onnxruntime==1.31.1 torch==2.15.0 transformers==4.57.6 uroman==1.3.1.1
python3 scripts/generate.py /path/to/assets supertonic3
python3 scripts/generate.py /path/to/assets mms
```

가져온 모델의 청취용 MP3를 만들 때는 저장소 루트에서 `python3 scripts/listening_copies.py /path/to/ffmpeg`를 실행한 뒤 listen 디렉터리도 함께 커밋한다.
