def two(arr,x):
    '''

    :param arr: 从小到大的数组
    :param x: 查找值
    :return: 返回索引
    '''
    length=len(arr)
    mid=int(length/2)
    #print(arr[mid])
    left=0
    right=length-1
    for i in range(int(length/2)):
        if x<arr[mid]:
            right=mid-1
        elif x>arr[mid]:
            left=mid+1
        else:
            break
        mid=int((right+left)/2)
        #print(mid,right,left)
    if i<length/2:
        return mid
    else:
        return None
print('查找值的索引是：',two([1,2,3,4],4))