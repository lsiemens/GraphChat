import { Vec2 } from "./Vec2";

export class Prompt {
  public model: string;
  public upstream: string[];
  public content: string;
  public position: Vec2;

  constructor(model: string, position: Vec2 = new Vec2()) {
    this.model = model;
    this.upstream = [];
    this.content = "";
    this.position = position;
  }
}
