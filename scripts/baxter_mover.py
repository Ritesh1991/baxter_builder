#!/usr/bin/env python


import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg 
import baxter_interface
from baxter_interface import Gripper

from std_msgs.msg import (Header, String)
from geometry_msgs.msg import (PoseStamped, Pose, Point, Quaternion)
from baxter_core_msgs.msg import DigitalIOState

from moveit_commander import MoveGroupCommander

block1_flag = False
block2_flag = False
block3_flag = False
sleep_flag = True
xpos_up = 0
ypos_up = 0


def init():
    #Wake up Baxter
    baxter_interface.RobotEnable().enable()
    rospy.sleep(0.25)
    print "Baxter is enabled"

    #Taken from the MoveIt Tutorials
    moveit_commander.roscpp_initialize(sys.argv)
    robot = moveit_commander.RobotCommander()

    global scene
    scene = moveit_commander.PlanningSceneInterface()

    #Activate Left Arm to be used with MoveIt
    global group
    group = MoveGroupCommander("left_arm")
    
    global left_gripper
    left_gripper = baxter_interface.Gripper('left')
    left_gripper.calibrate()

    pose_target = geometry_msgs.msg.Pose()
     #moving back to vision place
    print "Moving to Vision State"
    pose_target.orientation.x = 1
    pose_target.position.x = 0.782
    pose_target.position.y = 0.227
    pose_target.position.z = -0.112
    group.set_pose_target(pose_target)
    plan5 = group.plan()
    group.go(wait=True)
    rospy.sleep(2)


def move_block(xpos_up, ypos_up, zpos_up, zpos_down):
    pose_target = geometry_msgs.msg.Pose()

    pose_target.orientation.x = 1 
    pose_target.position.x = xpos_up
    pose_target.position.y = ypos_up
    pose_target.position.z = zpos_up
    group.set_pose_target(pose_target)
    plan1 = group.plan()
    group.go(wait=True)
    rospy.sleep(2)

    #Close Baxter's left gripper
    left_gripper.close()
    rospy.sleep(2)

    print "Going to middle pose"
    pose_target.orientation.x = 1
    pose_target.position.x = 0.7
    pose_target.position.y = 0.4
    pose_target.position.z = 0.3
    group.set_pose_target(pose_target)
    plan2 = group.plan()
    group.go(wait=True)
    rospy.sleep(2)


    #Open Baxter's left gripper to drop in box
    left_gripper.open()
    rospy.sleep(2)


    #Waypoint to vision place
    print "Moving to Vision State"
    pose_target.orientation.x = 1
    pose_target.position.x = 0.85
    pose_target.position.y = 0.1
    pose_target.position.z = 0.1
    group.set_pose_target(pose_target)
    plan4 = group.plan()
    group.go(wait=True)
    rospy.sleep(2)

def read_pos(Point):
    # print "in read_pos"
    global xpos_up, ypos_up
    xpos_up = Point.x
    ypos_up = Point.y


def block_counter(count):
    print "In block_counter"
    global block1_flag, block2_flag, block3_flag
    block1_flag = False
    block2_flag = False
    block3_flag = False
    
    if count == 1:
        print "Setting block1_flag"
        block1_flag = True
    elif count == 2:
        print "Setting block2_flag"
        block2_flag = True
    elif count == 3:
        print "Setting block3_flag"
        block3_flag = True


def checkButton(msg):
    global sleep_flag
    sleep_flag = True
    if msg.state == True:
        sleep_flag = False


def main():
    rospy.init_node('baxter_mover_node')

    print "Initializing all MoveIt related functions"
    init()

    print "Subscribing to center_of_object topic to receive points"
    rospy.Subscriber("/opencv/center_of_object", Point, read_pos)
    rospy.sleep(0.05)
   
    count = 1
    while not rospy.is_shutdown():
        block_counter(count)
        rospy.sleep(1)

        global block1_flag, block2_flag, block3_flag
        if block1_flag == True:
            zpos_up = 0.02
            zpos_down = -0.06

        if block2_flag == True:
            zpos_up = -0.02
            zpos_down = -0.02
        
        if block3_flag == True:
            zpos_up = -0.06
            zpos_down = 0.02

        print xpos_up, ypos_up, zpos_up, zpos_down
        
        move_block(xpos_up, ypos_up, zpos_up, zpos_down)

        count = count +1

        global sleep_flag
        sleep_flag = True

        if count > 3:
            #time to reset blocks
            print "Sleeping"

            while sleep_flag:
                pass
            
            count = 1


if __name__ == '__main__':
    main()