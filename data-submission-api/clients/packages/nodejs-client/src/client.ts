import axios, { AxiosProxyConfig, AxiosRequestConfig } from "axios";

import { ClientDeviceInfo, RequiredRequestHeaders, Submission, TagDatum } from "./models";

/**
 * Configuration type provided to the WaterlyConnectApiClient constructor.
 */
export type WaterlyConnectApiClientConfig = {
  /**
   * The endpoint URL for the WaterlyConnect service, provided by the Waterly team.
   * This will typically be of the form:  https://host.name/connect/submit
   *
   * Please see the Waterly team if you need assistance with this value.
   */
  url: string;

  /**
   * The unique client secret WaterlyConnect service, provided by the Waterly team.
   * This is usually a 32 character string.  Please use secure transmission and storage methods to
   * manage this value.
   *
   * Please see the Waterly team if you need assistance with this value.
   */
  clientToken: string;

  /**
   * Details concerning the client device submitting the data to WaterlyConnect. At minimum, two fields of
   * this object are required:  id and type.
   *   - id: A unique device id provided to you by the Waterly team.
   *   - type: A description of the connecting device or system.  For instance, "Ewon Flexy", or "SCADA 123"
   *
   * Please see the Waterly team if you need assistance with this value.
   */
  clientDevice: ClientDeviceInfo;

  /**
   * (Optional) If the API client is behind a proxy, it may be configured here.
   */
  proxy?: AxiosProxyConfig;
};

export class WaterlyConnectApiClient {
  private readonly clientDevice: ClientDeviceInfo;

  private readonly axiosConfigTemplate: Omit<AxiosRequestConfig<Submission>, "data">;

  constructor(config: WaterlyConnectApiClientConfig) {
    const { url, proxy, clientToken, clientDevice } = config;
    this.clientDevice = clientDevice;

    const headers: RequiredRequestHeaders = {
      "x-waterly-connect-token": clientToken,
      "x-waterly-request-type": "WaterlyConnect",
    };

    this.axiosConfigTemplate = {
      url,
      method: "post",
      headers,
      proxy,
    };
  }

  public async submitData(tags: TagDatum[]) {
    const submission: Submission = {
      tags,
      device: this.clientDevice,
      timestamp: Math.floor(new Date().getTime() / 1000),
    };

    const requestConfig: AxiosRequestConfig<Submission> = {
      ...this.axiosConfigTemplate,
      data: submission,
    };

    await axios(requestConfig);
  }
}
