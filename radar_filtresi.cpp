#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"

class RadarFiltresi : public rclcpp::Node {
public:
    RadarFiltresi() : Node("radar_filtresi_node") {
        subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "turtle1/pose", 10, std::bind(&RadarFiltresi::pose_callback, this, std::placeholders::_1));
        RCLCPP_INFO(this->get_logger(), "İNÜFEST: C++ Radar Filtresi Aktif (Yüksek Hız Modu).");
    }

private:
    void pose_callback(const turtlesim::msg::Pose::SharedPtr msg) const {
        // C++ burada radar verilerini işliyor
        if (msg->x > 7.0 || msg->y > 3.0) {
            RCLCPP_WARN(this->get_logger(), "KRİTİK: İHA Sınırda! Konum: X=%.2f, Y=%.2f", msg->x, msg->y);
        }
    }
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
};

int main(int argc, char * argv[]) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<RadarFiltresi>());
    rclcpp::shutdown();
    return 0;
}