import { Input } from "../components/Input";
function LoginForm() {
  const onSubmitForm = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };
  return (
    <form onSubmit={onSubmitForm}>
      <Input type="text" label="username" />
      <Input type="password" label="password" />
      <button type="button">Click Here</button>
    </form>
  );
}

export { LoginForm };
