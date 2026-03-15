#include <memory>

#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>

using std::placeholders::_1;

class OdomToTF : public rclcpp::Node {
    public:
        OdomToTF() : Node("odom_to_tf") {
            frame_id = this->declare_parameter("frame_id", std::string("odom"));
            child_frame_id = this->declare_parameter("child_frame_id", std::string("base_link"));
            std::string odom_topic = this->declare_parameter("odom_topic", std::string("odom"));
            
            RCLCPP_INFO(this->get_logger(), "Subscribing to odom_topic: %s", odom_topic.c_str());
            RCLCPP_INFO(this->get_logger(), "Broadcasting TF: %s -> %s", frame_id.c_str(), child_frame_id.c_str());

            // Using default QoS which is usually compatible with the bridge's reliable setting, 
            // but also allowing SensorData (Best Effort) if that's what Gazebo provides.
            sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
                odom_topic, 
                rclcpp::SystemDefaultsQoS(), 
                std::bind(&OdomToTF::odomCallback, this, _1));
            
            tfb_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);
        }
    private:
        std::string frame_id, child_frame_id;
        std::shared_ptr<tf2_ros::TransformBroadcaster> tfb_;
        rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr sub_;
        
        void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) const {
            geometry_msgs::msg::TransformStamped tfs_;
            
            // Use the timestamp from the message to ensure TF synchronization
            tfs_.header.stamp = msg->header.stamp;
            tfs_.header.frame_id = frame_id;
            tfs_.child_frame_id = child_frame_id;
            
            tfs_.transform.translation.x = msg->pose.pose.position.x;
            tfs_.transform.translation.y = msg->pose.pose.position.y;
            tfs_.transform.translation.z = msg->pose.pose.position.z;
            tfs_.transform.rotation = msg->pose.pose.orientation;

            tfb_->sendTransform(tfs_);
            
            // Periodically log to confirm the node is active
            RCLCPP_DEBUG(this->get_logger(), "Published transform %s -> %s", 
                         frame_id.c_str(), child_frame_id.c_str());
        }
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<OdomToTF>());
    rclcpp::shutdown();
    return 0;
}
