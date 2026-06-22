import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
};
//Jetson -> '10.42.0.124'
module.exports = {
    allowedDevOrigins: ['10.42.0.124']
}
export default nextConfig;
