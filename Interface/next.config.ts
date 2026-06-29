import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};
//Jetson -> '10.42.0.124, 10.42.0.1'
//rokoko -> 10.54.132.8,10.54.132.13,10.42.0.122
module.exports = {
    allowedDevOrigins: ['10.42.0.1','10.42.0.124','10.54.132.8','10.225.60.141','10.54.132.13','10.42.0.122']
}
export default nextConfig;
