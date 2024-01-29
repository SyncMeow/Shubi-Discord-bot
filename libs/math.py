def combination(elements:list[any],count:int)->list[any]:
  n:int = len(elements)
  tmp = []
  ans = []
  if count > n: 
    raise ValueError("The count is bigger than the size of giving elements")

  def f(last:int,k:int):
    if n - last < k:
      return
    if k == 0:
      ans.append(' '.join(tmp))
    else:
      tmp.append(elements[last])
      f(last + 1, k -1)
      tmp.pop()

      f(last + 1, k)
  f(0,count)
  return ans
      
ele = "a b c d e f g h".split(' ')
combination(ele, 5)
 