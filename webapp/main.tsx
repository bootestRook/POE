import React from "react";
import { createRoot } from "react-dom/client";
import { App, clearLaunchCacheIfRequested } from "./App";
import "./styles.css";

clearLaunchCacheIfRequested();

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
