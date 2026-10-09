export class ServerError extends Error {
  constructor(
    type: string,
    message: string) {
      super(`${type} => ${message}`);
      this.name = "ServerError";
  }
}
