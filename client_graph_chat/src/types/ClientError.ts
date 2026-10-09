export interface Status {
  readonly message: string,
  readonly details: string,
}

export class ClientError extends Error {
  public status: Status;
  
  constructor( brief: string, message: string) {
    super(message);
    this.name = "ClientError";
    this.status = {
      message: brief,
      details: message,
    };
  }
}

