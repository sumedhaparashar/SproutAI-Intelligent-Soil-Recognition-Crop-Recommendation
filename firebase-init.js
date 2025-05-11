// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyC2xX4eDFO8xtEYZdPWPauqFbKGoC5craY",
  authDomain: "growsure-40db7.firebaseapp.com",
  projectId: "growsure-40db7",
  storageBucket: "growsure-40db7.firebasestorage.app",
  messagingSenderId: "740161753172",
  appId: "1:740161753172:web:424246f51acfa9f497ddc1",
  measurementId: "G-2XS1GP18GW"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);