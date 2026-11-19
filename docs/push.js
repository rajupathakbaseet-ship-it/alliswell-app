/* All Is Well Rashifal – Web Push (OneSignal)
   सभी पेज इसी एक फ़ाइल को लोड करते हैं। App ID बदलनी हो तो सिर्फ़ यहीं बदलें। */
(function () {
  var APP_ID = "37b155be-4347-489b-a539-798a1ffe7885"; // OneSignal App ID
  var SAFARI_ID = "web.onesignal.auto.6401d2fc-b951-4213-a02c-03159c046b78";
  if (!APP_ID || !("Notification" in window)) return;

  var en = location.pathname.indexOf("/en/") === 0 ||
    (document.documentElement.lang || "").toLowerCase().indexOf("en") === 0;

  var T = en ? {
    msg: "Get today's horoscope and planet transit (gochar) alerts from Pandit Raju Pathak every morning.",
    yes: "Yes, allow", no: "Later",
    welcomeTitle: "All Is Well Rashifal",
    welcome: "Thank you! You will now get daily horoscope updates.",
    bell: "Get daily horoscope alerts"
  } : {
    msg: "पंडित राजू पाठक से रोज़ सुबह आज का राशिफल और ग्रह गोचर की खबरें पाने के लिए अनुमति दें।",
    yes: "हाँ, अनुमति दें", no: "बाद में",
    welcomeTitle: "All Is Well Rashifal",
    welcome: "धन्यवाद! अब आपको रोज़ का राशिफल मिलता रहेगा।",
    bell: "रोज़ का राशिफल पाएँ"
  };

  window.OneSignalDeferred = window.OneSignalDeferred || [];
  OneSignalDeferred.push(async function (OneSignal) {
    await OneSignal.init({
      appId: APP_ID,
      safari_web_id: SAFARI_ID,
      serviceWorkerPath: "/OneSignalSDKWorker.js",
      serviceWorkerParam: { scope: "/" },
      allowLocalhostAsSecureOrigin: false,
      welcomeNotification: { title: T.welcomeTitle, message: T.welcome },
      notifyButton: {
        enable: true, position: "bottom-left", size: "medium", showCredit: false,
        text: {
          "tip.state.unsubscribed": T.bell,
          "tip.state.subscribed": en ? "You are subscribed" : "आप जुड़ चुके हैं",
          "tip.state.blocked": en ? "Notifications are blocked" : "नोटिफिकेशन बंद हैं",
          "message.prenotify": T.bell,
          "message.action.subscribed": T.welcome,
          "message.action.resubscribed": T.welcome,
          "message.action.unsubscribed": en ? "You won't get notifications" : "अब नोटिफिकेशन नहीं आएँगे",
          "dialog.main.title": "All Is Well Rashifal",
          "dialog.main.button.subscribe": en ? "SUBSCRIBE" : "जुड़ें",
          "dialog.main.button.unsubscribe": en ? "UNSUBSCRIBE" : "हटें",
          "dialog.blocked.title": en ? "Unblock notifications" : "नोटिफिकेशन चालू करें",
          "dialog.blocked.message": en ? "Allow notifications from browser settings." : "ब्राउज़र की सेटिंग में जाकर नोटिफिकेशन की अनुमति दें।"
        }
      },
      promptOptions: {
        slidedown: {
          prompts: [{
            type: "push",
            autoPrompt: true,
            text: { actionMessage: T.msg, acceptButton: T.yes, cancelButton: T.no },
            delay: { pageViews: 1, timeDelay: 6 }
          }]
        }
      }
    });
    try { OneSignal.User.addTag("lang", en ? "en" : "hi"); } catch (e) {}
  });

  var s = document.createElement("script");
  s.src = "https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js";
  s.defer = true;
  document.head.appendChild(s);
})();
