import { Vec2 } from "./Vec2";

export class Node {
  readonly id: string;
  readonly upstream: string[];
  readonly request: string;
  readonly reply: string;
  readonly model: string;
  readonly costUSD: number | null;
  public position: Vec2;

  constructor(
      id: string,
      upstream: string[],
      request: string,
      reply: string,
      model: string,
      costUSD: number | null,
      position: Vec2 = new Vec2()) {
    this.id = id;
    this.upstream = upstream;
    this.request = request;
    this.reply = reply;
    this.model = model;
    this.costUSD = costUSD;
    this.position = position;
  }
}
