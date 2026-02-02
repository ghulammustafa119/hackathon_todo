export interface LoginResponse {
  token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
  };
}

export interface RegisterResponse {
  message: string;
}