  // Import the functions you need from the SDKs you need
importScripts('https://www.gstatic.com/firebasejs/9.21.0/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/9.21.0/firebase-messaging.js');

  // TODO: Add SDKs for Firebase products that you want to use
  // https://firebase.google.com/docs/web/setup#available-libraries
const firebaseConfig = {
  apiKey: "AIzaSyB377d4_AFRtoEIjpN2Puf3CYwe-I9dCGE",
  authDomain: "vff-group-b185c.firebaseapp.com",
  projectId: "vff-group-b185c",
  storageBucket: "vff-group-b185c.appspot.com",
  messagingSenderId: "711189707453",
  appId: "1:711189707453:web:3813986a11e36f830b55d4",
  measurementId: "G-YYEJHD2GJ1"
};
console.log("firebase_config::"+firebaseConfig);
  // Initialize Firebase app

  // Initialize Firebase app in the service worker
firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();
console.log("messaging::"+messaging);
// Customize notification behavior when the app is in the background
messaging.setBackgroundMessageHandler((payload) => {
  console.log('Background Message:', payload);
  // Customize the behavior when the app is in the background
  // You might want to show a notification using the Notification API
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});
