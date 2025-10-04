import React from "react";

const Message = ({ type, text }) => {
  if (!text) return null;
  const color = type === "error" ? "red" : "green";
  return <p style={{ color }}>{text}</p>;
};

export default Message;
