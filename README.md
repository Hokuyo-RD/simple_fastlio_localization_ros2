# simple_fastlio_localization

## 概要
このパッケージは、3D LiDAR (LIO) のオドメトリと点群を使用して、事前に作成された3D地図 (PCD) 上での自己位置推定 (Localization) を行うROS 2ノードを提供します。
FastLIOなどのLIOアルゴリズムからの出力を用いて、地図とのマッチングを行い、補正された位置姿勢を出力します。

---

## 目次
- [simple\_fastlio\_localization](#simple_fastlio_localization)
  - [概要](#概要)
  - [目次](#目次)
  - [インストール](#インストール)
  - [ノード: localization\_node](#ノード-localization_node)
    - [パラメータ](#パラメータ)
      - [トピック (Subscribers)](#トピック-subscribers)
      - [トピック (Publishers)](#トピック-publishers)
  - [実行方法](#実行方法)
    - [Launchファイルによる起動](#launchファイルによる起動)
      - [主なLaunch引数](#主なlaunch引数)

---

## インストール

```bash
cd <YOUR-ROS2-WORKSPACE>/src
git clone --recurse -b ROS2 https://github.com/kiyoshiiriemon/simple_fastlio_localization/
cd ../
rosdep install --from-paths src/simple_fastlio_localization --ignore-src -r -y
colcon build --symlink-install --packages-select simple_fastlio_localization
```

## ノード: localization_node

### パラメータ

| パラメータ名 | 型 | デフォルト値 | 説明 |
| --- | --- | --- | --- |
| `map_file` | string | `""` | **(必須)** 3D地図ファイル (.pcd) へのパス。 |
| `initial_pose` | string | `""` | 初期位置姿勢。`"x y z qx qy qz qw"` の形式の文字列。 |
| `frames_accumulate` | int | `1` | マッチングのために蓄積する点群のフレーム数。 |
| `min_registration_distance` | double | `0.0` | レジストレーションを実行する最小移動距離 [m]。 |
| `asynchronous_registration` | bool | `false` | 非同期でレジストレーションを行うかどうか。(処理が重たくなるので、falseを推奨します。) |
| `publish_2d_pose` | bool | `false` | 2D姿勢 (`map` -> `odom` 変換) を配信するかどうか。Nav2などで使用する場合に有効にします。 |
| `visualize_registration_result` | bool | `false` | レジストレーション結果（成功/失敗）に応じて点群の色を変えて可視化するかどうか。 |
| `enable_sound` | bool | `false` | レジストレーション結果を効果音で通知するかどうか。 |
| `enable_lio_only_update` | bool | `false` | 点群マッチングがない間、LIOオドメトリのみで更新を続けるかどうか。(lioがimu周期の場合trueが必須。) |

#### トピック (Subscribers)

| トピック名 | 型 | 説明 |
| --- | --- | --- |
| `/Odometry` | `nav_msgs/Odometry` | LIOアルゴリズムからのオドメトリ入力。 |
| `/cloud_registered` | `sensor_msgs/PointCloud2` | LIO座標系での点群入力。 |

※ Launchファイル等でリマップ可能です。

#### トピック (Publishers)

| トピック名 | 型 | 説明 |
| --- | --- | --- |
| `/estimated_pose` | `geometry_msgs/PoseStamped` | 推定された地図座標系での位置姿勢。 |
| `/map_cloud` | `sensor_msgs/PointCloud2` | 読み込んだ地図点群 (Latched)。 |
| `/loc_registered_cloud` | `sensor_msgs/PointCloud2` | マッチングに使用された登録点群（可視化用）。 |
| `/tf` | `tf2_msgs/TFMessage` | `map` -> `odom` (またはLIOフレーム) のTF変換。 |

## 実行方法

### Launchファイルによる起動

`localization.launch` を使用して起動します。パラメータはYAMLファイルまたは引数で指定できます。

```bash
export MAP_DIR=<地図のディレクトリ>

ros2 launch simple_fastlio_localization localization.launch \
    map_file:=$MAP_DIR/toyonaka.pcd \
    initial_pose:="0 0 0 0 0 0 1" \
    odom_topic:=/hokuyo_lio/lidar_odom \
    cloud_odom_topic:=/hokuyo_lio/aligned_scan_points \
    rviz:=true
```

#### 主なLaunch引数

- `map_file`: 地図ファイルのパス。
- `initial_pose`: 初期位置姿勢 ("x y z qx qy qz qw")。
- `odom_topic`: LIOのトピック名。
- `cloud_odom_topic`: LIO点群のトピック名。
- `rviz`: RViz2を同時に起動するかどうか。
- `param_file_path`: パラメータファイルのパス (デフォルトは `config/localization_params.yaml`)。