import {
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputRightElement,
  Button,
} from "@chakra-ui/react";
import { useState } from "react";

function LoginPage() {
  return (
    <form className="">
      <div className="w-3/12">
        <FormControl id="username">
          <FormLabel>Email address</FormLabel>
          <Input />
        </FormControl>
        <FormControl>
          <FormLabel>Password</FormLabel>
          <PasswordInput />
        </FormControl>
      </div>
    </form>
  );
}

function PasswordInput() {
  const [show, setShow] = useState(false);
  const handleClick = () => setShow(!show);

  return (
    <InputGroup size="md">
      <Input
        pr="4.5rem"
        type={show ? "text" : "password"}
        placeholder="Enter password"
      />
      <InputRightElement width="4.5rem">
        <Button h="1.75rem" size="sm" onClick={handleClick}>
          {show ? "Hide" : "Show"}
        </Button>
      </InputRightElement>
    </InputGroup>
  );
}

export { LoginPage };
