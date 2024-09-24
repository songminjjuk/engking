import React from "react";
import { ClockLoader } from "react-spinners";

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0, 0, 0, 0.5)", // Semi-transparent background
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 9999, // Ensures the spinner is on top of everything
};

const Loading = ({ loading }) => {
  if (!loading) return null; // Don't render the component if loading is false

  return (
    <div style={overlayStyle}>
      <ClockLoader color="#f7a8c5" loading={loading} size={80} />
    </div>
  );
};

export default Loading;
