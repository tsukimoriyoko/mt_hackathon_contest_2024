import { TTSSource, TTSConfigItem, AgentVoice } from './constants';
import { ssmlParser, msSSMLParser } from './ssmlParser';

const ttsState = {
  isPlaying: false,
  isSynthing: false,
  isCanceled: false,
  isSuccess: false,
};

const sampleRate = 24000;
let player: any | null = null;
let accessToken = null;

/**
 * @doc https://docs.sankuai.com/ai-speech/guide/auth/
 *  tts鉴权 获取token
 */
function getAccessTokenApi(success?: (result: any) => void, fail?: (err: any) => void) {
  wx.request({
    url: 'https://auth-ai.vip.sankuai.com/oauth/v2/token',
    method: 'POST',
    data: {
      grant_type: 'client_credentials',
      client_id: 'cYv/61fSOJPhlMebCH2rTdZKSzVaHiDL2Z/X2n1eGGY=',
      client_secret: 'e5c8565682854c0e864ed508cdd91204',
    },
    header: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    success(res) {
      if (success) {
        success(res);
      }
      console.log(res.data);
    },
    fail(err) {
      if (fail) {
        fail(err);
      }
    },
  });
}

/**
 *  llm-tts鉴权 获取token
 */
function getLLMAccessTokenApi(success?: (result: any) => void, fail?: (err: any) => void) {
  wx.request({
    url: 'https://auth-ai.vip.sankuai.com/oauth/v2/token',
    method: 'POST',
    data: {
      grant_type: 'client_credentials',
      client_id: 'cYv/61fSOJPhlMebCH2rTdZKSzVaHiDL2Z/X2n1eGGY=',
      client_secret: 'e5c8565682854c0e864ed508cdd91204',
    },
    header: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    success(res) {
      if (success) {
        success(res);
      }
      console.log(res.data);
    },
    fail(err) {
      if (fail) {
        fail(err);
      }
    },
  });
}

function guid() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    var r = (Math.random() * 16) | 0,
      v = c == 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

// 流式合成 TTS https://docs.sankuai.com/ai-speech/tts/online/platform_http/#_8
// 微软流式合成 TTS https://km.sankuai.com/collabpage/1551687576#id-%E6%B5%81%E5%BC%8F%E5%90%88%E6%88%90%E6%8E%A5%E5%8F%A3(%E5%BE%AE%E8%BD%AF)
export function ttsStream(
  token: string,
  text: string,
  voice_name: string,
  volume: number,
  speed: number,
  sampleRate: number,
  vendor: string,
  success?: (result: any) => void,
  fail?: (err: any) => void,
) {
  const sessionId = guid();
  const params = {
    text,
    voice_name,
    speed,
    volume,
    sample_rate: sampleRate,
    audio_format: 'mp3',
    enable_extra_volume: 0,
  };
  // 强化音量开关，打开后合成音将获得更高的音量，0:关闭(默认)，1:打开
  params.enable_extra_volume = volume === 100 ? 1 : 0;
  let url;
  switch (vendor) {
    case TTSSource.MEITUAN:
      url = '/tts/v1/stream';
      break;
    case TTSSource.MEITUAN_LLM:
      url = '/tts/v1/stream';
      break;
    case TTSSource.MICROSOFT:
      url = '/tts/v1/proxy/stream';
      break;
    default:
      url = '/tts/v1/stream';
      break;
  }
  // url = '/tts/v1/synthesis';
  // const TTSHost = 'https://aispeech.sankuai.com';
  console.log('ttsStream', ...arguments);
  console.log('ttsStream', 'https://speech.meituan.com' + url);

  wx.request({
    url: 'https://speech.meituan.com' + url,
    responseType: 'arraybuffer',
    method: 'POST',
    data: params,
    header: {
      // 'TARGET': TTSHost + url,
      'Cache-Control': 'no-cache',
      SessionId: sessionId,
      Token: token,
      // 'Set': vendor === TTSSource.MICROSOFT ? 'proxy-ms' : ''
    },
    success(res) {
      if (success) {
        success(res);
      }
      console.log(res.data);
    },
    fail(err) {
      if (fail) {
        fail(err);
      }
    },
  });
}

// 初始化player
function ttsInit() {
  if (player) {
    player.pause();
  } else {
    player = wx.createInnerAudioContext();
    player.autoplay = true;
    wx.setInnerAudioOption({
      obeyMuteSwitch: false, // 设置声音播放不受iOS静音开关控制
    });
  }
  console.log('tts init');
  getLLMAccessTokenApi(
    (result) => {
      accessToken = result.data.data.access_token;
      // wx.showToast({ title: 'Token获取成功' });
      console.log('getLLMAccessTokenApi', result.data);
    },
    (err) => {
      // wx.showToast({ title: 'Token获取失败，请重试' });
      console.log('getLLMAccessTokenApi err', err);
    },
  );
}

// 处理返回的pcm
function handleResponse(response: any) {
  if (response) {
    if (ttsState.isCanceled === false) {
      if (ttsState.isPlaying === false) {
        ttsState.isPlaying = true;
      }
      let path = wx.env.USER_DATA_PATH + '/tts.mp3';
      wx.getFileSystemManager().writeFile({
        filePath: path,
        data: response.data,
        encoding: 'binary',
        success(res) {
          console.log('文件保存成功', res);
          toPlayTTS(path);
          // wx.openDocument({
          //   filePath: path,
          //   encoding: 'binary',
          //   success: function (res) {
          //     console.log('打开文档成功')
          //   },
          // });
        },
        fail(err) {
          console.log('文件保存失败', err);
        },
      });
    }
  }
  if (ttsState.isCanceled === false) {
    if (ttsState.isSynthing) {
      ttsState.isSynthing = false;
      ttsState.isSuccess = true;
    }
  }
  console.log('handleResponse', response);
}

// 报错处理
function handleError(error: any) {
  if (ttsState.isCanceled === false) {
    if (ttsState.isSynthing) {
      stop();
      ttsState.isSynthing = false;
      ttsState.isPlaying = false;
      ttsState.isSuccess = true;
    }
  }
  console.log('handleError', error);
}

// 音色播放
function ttsStart(voice: AgentVoice, text: string) {
  if (!text || !accessToken) {
    console.log(`tts start fail, text: ${text}, token: ${accessToken}`);
    return;
  }
  ttsState.isCanceled = false;
  const styleParams = {
    voiceName: voice.voiceName,
    domain: voice.domain,
    emotion: voice.emotion,
    character: voice.character,
    volume: voice.volume,
    speed: voice.speed,
  };
  const ttsConfig: TTSConfigItem = JSON.parse(voice.ttsConfig ?? '{}');
  const ssml = ssmlParser(text, styleParams);
  const msSSML = msSSMLParser(text, styleParams);
  ttsStream(
    accessToken,
    ttsConfig.vendor === TTSSource.MICROSOFT ? msSSML : ssml,
    voice.voiceName,
    voice.volume,
    voice.speed,
    sampleRate,
    ttsConfig.vendor,
    handleResponse,
    handleError,
  );
}

// 播放
function toPlayTTS(filePath: string) {
  if (!player) {
    ttsInit();
  }
  player.src = filePath;
  player.onPlay(() => {
    console.log('playTTS 开始播放');
  });
  player.onError((error: any) => {
    console.log('playTTS onError', error);
  });
}

// 停止播放
function ttsStop() {
  ttsState.isCanceled = true;
  if (player) {
    player.pause();
  }
}

export { ttsInit, ttsStart, ttsStop, getAccessTokenApi, getLLMAccessTokenApi };
