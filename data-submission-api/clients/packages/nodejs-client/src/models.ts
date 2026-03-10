import { components, operations } from "./generated/schema";

export type TagDatum = components["schemas"]["TagDatum"];
export type Submission = components["schemas"]["WaterlyConnectSubmission"];
export type ClientDeviceInfo = components["schemas"]["Device"];
export type RequiredRequestHeaders = operations["submitData"]["parameters"]["header"];
