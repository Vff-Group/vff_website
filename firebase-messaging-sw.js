importScripts("https://www.gstatic.com/firebasejs/10.5.0/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/10.5.0/firebase-messaging.js");

const firebaseConfig = {
    apiKey: "AIzaSyB377d4_AFRtoEIjpN2Puf3CYwe-I9dCGE",
    authDomain: "vff-group-b185c.firebaseapp.com",
    projectId: "vff-group-b185c",
    storageBucket: "vff-group-b185c.appspot.com",
    messagingSenderId: "711189707453",
    appId: "1:711189707453:web:3813986a11e36f830b55d4",
    measurementId: "G-YYEJHD2GJ1"
  };


firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

messaging.setBackgroundMessageHandler(function (payload) {
  const notification = JSON.parse(payload.data.notification);
  const notificationOptions = {
    body: notification.body,
    icon: notification.icon
  };
  return self.registration.showNotification(notification.title, notificationOptions);
});
