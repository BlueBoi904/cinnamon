import { useState } from "react";

type InputType = {
  label: string;
  type: string;
};

function Input({ label, type }: InputType) {
  const [val, setval] = useState("");
  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setval(e.target.value);
  };
  return (
    <div>
      <label>{label}</label>
      <input type={type} value={val} onChange={onChange} />
    </div>
  );
}

export { Input };
