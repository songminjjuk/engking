import React, { useState } from "react";
import Loading from "./Loading"; // Adjust path if necessary

const TestPage = () => {
  const [loading, setLoading] = useState(false);

  const handleStartLoading = () => {
    setLoading(true);
    // Simulate an async operation like fetching data
    setTimeout(() => {
      setLoading(false);
    }, 3000); // Stop loading after 3 seconds
  };

  return (
    <div style={{ textAlign: "center", paddingTop: "50px" }}>
      <h1>Test Page with Loading Spinner</h1>
      <button onClick={handleStartLoading}>Start Loading</button>
      {/* The Loading component that displays an overlay spinner */}
      <Loading loading={loading} />
    </div>
  );
};

export default TestPage;
