import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};
//Jetson -> '10.42.0.124, 10.42.0.1'
//rokoko -> 10.54.132.65
module.exports = {
    allowedDevOrigins: ['10.42.0.1','10.42.0.124','*.local']
}
export default nextConfig;
