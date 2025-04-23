import math

D = 15.3 #cm
L_cam_0 = 634
R_cam_0 = 816
L_cam_FOV = 100.1590089*math.pi/180
R_cam_FOV = 101.3798244*math.pi/180
L_cam_resol = 1457
R_cam_resol = 1590
L_cam_degreeperpx = L_cam_FOV/L_cam_resol
R_cam_degreeperpx = R_cam_FOV/R_cam_resol
L_cam_target_left = int(input("L_cam_target_left: ")) #550 #leftD = 225,  #211 
L_cam_target_right = int(input("L_cam_target_right: ")) #1236 #RIGHTD = 248 #1361
R_cam_target_left = int(input("R_cam_target_left: ")) #340 #leftD = 269 #142 #96
R_cam_target_right = int(input("R_cam_target_right: ")) #965 #RIGHTD = 12 #1134

"""
L_cam_target_left = L_cam_0 - L_cam_target_left
L_cam_target_right = L_cam_0 + L_cam_target_right
R_cam_target_left = R_cam_0 - R_cam_target_left
R_cam_target_right = R_cam_0 + R_cam_target_right
"""




L_cam_target_left_degree = math.fabs(L_cam_0 - L_cam_target_left)*L_cam_degreeperpx
R_cam_target_left_degree = math.fabs(R_cam_0 - R_cam_target_left)*R_cam_degreeperpx
target_left_height = float(D/(math.tan(R_cam_target_left_degree)-math.tan(L_cam_target_left_degree)))
print(target_left_height)

L_cam_target_right_degree = math.fabs(L_cam_0 - L_cam_target_right)*L_cam_degreeperpx
R_cam_taget_right_degree = math.fabs(R_cam_0 - R_cam_target_right)*R_cam_degreeperpx
target_right_height = float(D/(math.tan(L_cam_target_right_degree)-math.tan(R_cam_taget_right_degree)))
print(target_right_height)

R_cam_target_right_distance = target_right_height/math.cos(R_cam_taget_right_degree)
R_cam_target_left_distance = target_left_height/math.cos(R_cam_target_left_degree)

target_length = math.sqrt(R_cam_target_right_distance**2 + R_cam_target_left_distance**2 - 2*R_cam_target_right_distance*R_cam_target_left_distance*math.cos(R_cam_taget_right_degree + R_cam_target_left_degree))
print(f"Resultant length: {target_length}")